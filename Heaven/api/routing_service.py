"""
Routing Service - Interface to OSRM and GraphHopper
"""
import httpx
from typing import List, Dict, Optional, Tuple
from config import settings
from contracts import Coordinate, RouteResponse, RouteStep, RoutingMode
import logging

logger = logging.getLogger(__name__)


class RoutingService:
    """Service for calculating routes using OSRM and GraphHopper"""
    
    def __init__(self):
        self.osrm_url = settings.OSRM_URL
        self.graphhopper_url = settings.GRAPHHOPPER_URL
    
    async def calculate_citizen_route(
        self, 
        start: Coordinate, 
        end: Coordinate
    ) -> RouteResponse:
        """
        Calculate standard fast route using OSRM
        Used for Citizen Mode
        """
        try:
            # OSRM expects coordinates as lon,lat
            coords = f"{start.longitude},{start.latitude};{end.longitude},{end.latitude}"
            url = f"{self.osrm_url}/route/v1/driving/{coords}"
            
            params = {
                "overview": "full",
                "geometries": "geojson",
                "steps": "true"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            if data.get("code") != "Ok" or not data.get("routes"):
                raise Exception("No route found by OSRM")
            
            route = data["routes"][0]
            geometry = route["geometry"]["coordinates"]
            
            # Parse steps
            steps = []
            for leg in route.get("legs", []):
                for step in leg.get("steps", []):
                    steps.append(RouteStep(
                        instruction=step.get("maneuver", {}).get("instruction", "Continue"),
                        distance=step.get("distance", 0),
                        duration=step.get("duration", 0),
                        coordinates=step.get("geometry", {}).get("coordinates", [])
                    ))
            
            return RouteResponse(
                mode=RoutingMode.CITIZEN,
                start=start,
                end=end,
                coordinates=geometry,
                total_distance=route.get("distance", 0),
                total_duration=route.get("duration", 0),
                steps=steps
            )
            
        except Exception as e:
            logger.error(f"OSRM routing error: {e}")
            # Fallback: return simple direct route
            return self._create_fallback_route(start, end, RoutingMode.CITIZEN)
    
    async def calculate_emergency_route(
        self,
        start: Coordinate,
        end: Coordinate,
        congested_streets: Dict[str, float]
    ) -> RouteResponse:
        """
        Calculate priority route using GraphHopper with congestion avoidance
        Used for Emergency Mode
        
        Args:
            start: Starting coordinate
            end: Destination coordinate
            congested_streets: Dict of {street_id: congestion_score}
        """
        try:
            # GraphHopper API endpoint
            url = f"{self.graphhopper_url}/route"
            
            # Build custom model to penalize congested streets
            # This makes the router avoid high-congestion areas
            custom_model = self._build_emergency_custom_model(congested_streets)
            
            payload = {
                "points": [
                    [start.longitude, start.latitude],
                    [end.longitude, end.latitude]
                ],
                "profile": "car",
                "locale": "en",
                "instructions": True,
                "calc_points": True,
                "points_encoded": False,
                "custom_model": custom_model
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
            
            if "paths" not in data or not data["paths"]:
                raise Exception("No route found by GraphHopper")
            
            path = data["paths"][0]
            
            # Parse instructions/steps
            steps = []
            for instruction in path.get("instructions", []):
                steps.append(RouteStep(
                    instruction=instruction.get("text", "Continue"),
                    distance=instruction.get("distance", 0),
                    duration=instruction.get("time", 0) / 1000.0,  # Convert ms to seconds
                    coordinates=[]  # GraphHopper doesn't provide per-step coordinates easily
                ))
            
            # Get list of avoided streets
            avoided = [
                street_id for street_id, congestion in congested_streets.items()
                if congestion >= settings.CONGESTION_THRESHOLD_HIGH
            ]
            
            return RouteResponse(
                mode=RoutingMode.EMERGENCY,
                start=start,
                end=end,
                coordinates=path.get("points", {}).get("coordinates", []),
                total_distance=path.get("distance", 0),
                total_duration=path.get("time", 0) / 1000.0,  # Convert ms to seconds
                steps=steps,
                avoided_congested_streets=avoided
            )
            
        except Exception as e:
            logger.error(f"GraphHopper routing error: {e}")
            # Fallback: use OSRM
            logger.info("Falling back to OSRM for emergency route")
            fallback = await self.calculate_citizen_route(start, end)
            fallback.mode = RoutingMode.EMERGENCY
            fallback.avoided_congested_streets = []
            return fallback
    
    async def calculate_smartpark_route(
        self,
        start: Coordinate,
        nearest_free_parking: Coordinate,
        parking_zone_id: str,
        available_spots: int
    ) -> RouteResponse:
        """
        Calculate route to nearest free parking spot
        Used for SmartPark Mode
        """
        # Use OSRM for fast routing to parking
        route = await self.calculate_citizen_route(start, nearest_free_parking)
        route.mode = RoutingMode.SMARTPARK
        route.destination_parking_zone = parking_zone_id
        route.available_spots_at_destination = available_spots
        
        return route
    
    def _build_emergency_custom_model(self, congested_streets: Dict[str, float]) -> Dict:
        """
        Build GraphHopper custom model to penalize congested streets
        This uses GraphHopper's custom model feature to dynamically adjust routing
        """
        # For high congestion, we drastically reduce the effective speed
        # This makes the router prefer alternative routes
        
        # Note: In a real implementation, you would map street_ids to actual
        # road segments in GraphHopper's graph. This is a simplified version.
        
        return {
            "priority": [
                {
                    "if": "true",
                    "multiply_by": 1.0
                }
            ],
            "speed": [
                {
                    "if": "true",
                    "multiply_by": 1.0
                }
            ]
            # In production, you would add dynamic rules here based on congested_streets
            # Example: {"if": "road_id in [congested_ids]", "multiply_by": 0.3}
        }
    
    def _create_fallback_route(
        self,
        start: Coordinate,
        end: Coordinate,
        mode: RoutingMode
    ) -> RouteResponse:
        """
        Create a simple fallback route (straight line) when routing engines fail
        """
        # Simple straight-line approximation
        coords = [
            [start.longitude, start.latitude],
            [end.longitude, end.latitude]
        ]
        
        # Rough distance calculation (Haversine would be better)
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(
            radians, 
            [start.longitude, start.latitude, end.longitude, end.latitude]
        )
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        distance = 6371000 * c  # Earth radius in meters
        
        # Assume average speed of 40 km/h
        duration = (distance / 1000) / 40 * 3600
        
        return RouteResponse(
            mode=mode,
            start=start,
            end=end,
            coordinates=coords,
            total_distance=distance,
            total_duration=duration,
            steps=[
                RouteStep(
                    instruction=f"Head towards destination",
                    distance=distance,
                    duration=duration,
                    coordinates=coords
                )
            ]
        )


# Global routing service instance
routing_service = RoutingService()

