"""
Core Business Logic Services for UrbanFlowAI
The "Brain" - Implements Live Status and Route Calculation
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from config import settings
from contracts import (
    LiveStatusResponse, StreetStatus, ParkingZoneSummary, 
    ParkingSpotStatus, EmergencyVehicleStatus, CongestionLevel,
    RouteRequest, RouteResponse, Coordinate, RoutingMode, ParkingStatus
)
from database import StreetSegmentDB, ParkingZoneDB, ParkingSpotDB, EmergencyVehicleDB
from redis_client import redis_client
from routing_service import routing_service

logger = logging.getLogger(__name__)


class UrbanFlowBrain:
    """
    The Brain - Core intelligence of UrbanFlowAI
    Implements the two main functions: Live Status and Route Calculation
    """
    
    def __init__(self):
        self.redis = redis_client
        self.router = routing_service
    
    # ========================================
    # FUNCTION 1: Live Status
    # ========================================
    
    async def get_live_status(self, db: Session) -> LiveStatusResponse:
        """
        Mission: Provide a real-time snapshot of the entire city
        
        Logic:
        1. Connect to Redis and get all latest facts
        2. Combine with persistent data from PostgreSQL
        3. Package into a single, clean JSON response
        """
        logger.info("Generating live city status...")
        
        # Get all real-time data from Redis
        traffic_data = self.redis.get_all_traffic_data()
        parking_data = self.redis.get_all_parking_data()
        emergency_data = self.redis.get_all_emergency_vehicles()
        
        # Get street information from database and combine with traffic
        streets = self._build_street_status(db, traffic_data)
        
        # Get parking information from database and combine with real-time status
        parking_zones, total_spots, free_spots = self._build_parking_status(db, parking_data)
        
        # Get emergency vehicle information
        emergency_vehicles = self._build_emergency_status(db, emergency_data)
        
        # Calculate average congestion
        avg_congestion = (
            sum(s.congestion_score for s in streets) / len(streets)
            if streets else 0.0
        )
        
        # Count active emergencies
        active_emergencies = sum(
            1 for v in emergency_vehicles 
            if v.status == "responding"
        )
        
        return LiveStatusResponse(
            streets=streets,
            average_congestion=avg_congestion,
            parking_zones=parking_zones,
            total_parking_spots=total_spots,
            total_free_spots=free_spots,
            emergency_vehicles=emergency_vehicles,
            active_emergencies=active_emergencies
        )
    
    def _build_street_status(
        self, 
        db: Session, 
        traffic_data: Dict[str, float]
    ) -> List[StreetStatus]:
        """Build street status list by combining DB and Redis data"""
        streets = []
        
        # Get all streets from database
        street_segments = db.query(StreetSegmentDB).all()
        
        for segment in street_segments:
            # Get congestion from Redis, default to 0.0 if not available
            congestion = traffic_data.get(segment.street_id, 0.0)
            
            # Determine congestion level
            if congestion >= 0.8:
                level = CongestionLevel.CRITICAL
            elif congestion >= settings.CONGESTION_THRESHOLD_HIGH:
                level = CongestionLevel.HIGH
            elif congestion >= settings.CONGESTION_THRESHOLD_MEDIUM:
                level = CongestionLevel.MEDIUM
            else:
                level = CongestionLevel.LOW
            
            # Parse geometry (simplified - in production use proper WKT parsing)
            # For now, create dummy coordinates
            coords = [
                [float(segment.street_id.split('_')[1]) * -73.98, 40.75],
                [float(segment.street_id.split('_')[1]) * -73.97, 40.76]
            ]
            
            streets.append(StreetStatus(
                street_id=segment.street_id,
                street_name=segment.street_name,
                congestion_score=congestion,
                congestion_level=level,
                coordinates=coords
            ))
        
        return streets
    
    def _build_parking_status(
        self,
        db: Session,
        parking_data: Dict[str, ParkingStatus]
    ) -> tuple[List[ParkingZoneSummary], int, int]:
        """
        Build parking status by combining DB and Redis data
        
        Vision Engine provides: {"SPOT_A1": "free", "SPOT_A2": "occupied", ...}
        We need to map these to our zones
        """
        
        # Get all parking zones from database
        zones = db.query(ParkingZoneDB).all()
        
        zone_summaries = []
        total_spots = 0
        total_free = 0
        
        for zone in zones:
            # Get all spots in this zone
            spots_in_zone = db.query(ParkingSpotDB).filter(
                ParkingSpotDB.zone_id == zone.zone_id
            ).all()
            
            # Count free spots
            # Vision Engine format: "SPOT_A1" (matches spot_id in database)
            free_in_zone = 0
            for spot in spots_in_zone:
                status = parking_data.get(spot.spot_id, ParkingStatus.UNKNOWN)
                if status == ParkingStatus.FREE:
                    free_in_zone += 1
            
            zone_total = len(spots_in_zone)
            occupancy = (zone_total - free_in_zone) / zone_total if zone_total > 0 else 0
            
            zone_summaries.append(ParkingZoneSummary(
                zone_id=zone.zone_id,
                zone_name=zone.zone_name,
                total_spots=zone_total,
                free_spots=free_in_zone,
                occupancy_rate=occupancy,
                latitude=zone.latitude,
                longitude=zone.longitude
            ))
            
            total_spots += zone_total
            total_free += free_in_zone
        
        return zone_summaries, total_spots, total_free
    
    def _build_emergency_status(
        self,
        db: Session,
        emergency_data: List
    ) -> List[EmergencyVehicleStatus]:
        """
        Build emergency vehicle status
        
        Vision Engine provides pixel coordinates, we need to convert or use directly
        Format: {"id": "truck_01", "location": [x, y], "bbox": [...], "timestamp": ...}
        """
        vehicles = []
        
        for data in emergency_data:
            # Get vehicle type from database
            vehicle = db.query(EmergencyVehicleDB).filter(
                EmergencyVehicleDB.vehicle_id == data.id
            ).first()
            
            vehicle_type = vehicle.vehicle_type if vehicle else "emergency_truck"
            
            # Convert pixel coordinates to lat/long if calibration is available
            # For now, use pixel coordinates directly or mock GPS coordinates
            # TODO: Implement proper pixel-to-GPS conversion based on camera calibration
            latitude = data.latitude if data.latitude else 40.7489  # Mock
            longitude = data.longitude if data.longitude else -73.9852  # Mock
            
            from datetime import datetime
            last_updated = datetime.fromtimestamp(data.timestamp)
            
            vehicles.append(EmergencyVehicleStatus(
                vehicle_id=data.id,
                vehicle_type=vehicle_type,
                latitude=latitude,
                longitude=longitude,
                heading=data.heading,
                speed=data.speed,
                status=data.status,
                last_updated=last_updated
            ))
        
        return vehicles
    
    # ========================================
    # FUNCTION 2: Route Calculation
    # ========================================
    
    async def calculate_route(
        self,
        request: RouteRequest,
        db: Session
    ) -> RouteResponse:
        """
        Mission: Be the smart navigator
        
        Logic:
        - Citizen Mode: Use fast OSRM routing
        - Emergency Mode: Use GraphHopper with congestion avoidance
        - SmartPark Mode: Route to nearest free parking
        """
        logger.info(f"Calculating route in {request.mode} mode...")
        
        if request.mode == RoutingMode.CITIZEN:
            return await self._calculate_citizen_route(request)
        
        elif request.mode == RoutingMode.EMERGENCY:
            return await self._calculate_emergency_route(request, db)
        
        elif request.mode == RoutingMode.SMARTPARK:
            return await self._calculate_smartpark_route(request, db)
        
        else:
            raise ValueError(f"Unknown routing mode: {request.mode}")
    
    async def _calculate_citizen_route(self, request: RouteRequest) -> RouteResponse:
        """
        Citizen Mode: Simple fast routing
        Uses OSRM for maximum speed
        """
        return await self.router.calculate_citizen_route(
            request.start,
            request.end
        )
    
    async def _calculate_emergency_route(
        self,
        request: RouteRequest,
        db: Session
    ) -> RouteResponse:
        """
        Emergency Mode: Intelligent priority routing
        
        Logic:
        1. Check live traffic data from Redis
        2. Ask GraphHopper for route, treating congested streets as slow/undesirable
        3. Return priority route that avoids traffic
        """
        # Get real-time traffic data
        traffic_data = self.redis.get_all_traffic_data()
        
        # Filter to get only highly congested streets
        congested_streets = {
            street_id: congestion
            for street_id, congestion in traffic_data.items()
            if congestion >= settings.CONGESTION_THRESHOLD_MEDIUM
        }
        
        logger.info(f"Found {len(congested_streets)} congested streets to avoid")
        
        # Calculate emergency route avoiding congestion
        return await self.router.calculate_emergency_route(
            request.start,
            request.end,
            congested_streets
        )
    
    async def _calculate_smartpark_route(
        self,
        request: RouteRequest,
        db: Session
    ) -> RouteResponse:
        """
        SmartPark Mode: Navigate to nearest free parking
        
        Logic:
        1. Find nearest parking zone with free spots
        2. Route to that location
        """
        # Get all parking data from Redis
        parking_data = self.redis.get_all_parking_data()
        
        # Find zones with free spots
        zones_with_free = {}
        for spot_key, status in parking_data.items():
            if status == ParkingStatus.FREE:
                # Extract zone from spot name (e.g., "SPOT_A1" -> "zone_A")
                # Format: SPOT_{ZONE_LETTER}{NUMBER}
                if spot_key.startswith("SPOT_"):
                    zone_letter = spot_key.split("_")[1][0]  # Get first char after SPOT_
                    zone_id = f"zone_{zone_letter}"
                    zones_with_free[zone_id] = zones_with_free.get(zone_id, 0) + 1
        
        if not zones_with_free:
            logger.warning("No free parking spots available")
            # Fallback to regular route
            route = await self.router.calculate_citizen_route(
                request.start,
                request.end
            )
            route.mode = RoutingMode.SMARTPARK
            route.available_spots_at_destination = 0
            return route
        
        # Find nearest zone with free spots
        # Simple approach: check all zones and pick closest
        nearest_zone = None
        min_distance = float('inf')
        
        for zone_id, free_count in zones_with_free.items():
            zone = db.query(ParkingZoneDB).filter(
                ParkingZoneDB.zone_id == zone_id
            ).first()
            
            if zone:
                # Calculate approximate distance
                distance = self._calculate_distance(
                    request.start,
                    Coordinate(latitude=zone.latitude, longitude=zone.longitude)
                )
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_zone = (zone, free_count)
        
        if nearest_zone:
            zone, free_count = nearest_zone
            parking_coord = Coordinate(
                latitude=zone.latitude,
                longitude=zone.longitude
            )
            
            return await self.router.calculate_smartpark_route(
                request.start,
                parking_coord,
                zone.zone_id,
                free_count
            )
        
        # Fallback
        return await self._calculate_citizen_route(request)
    
    def _calculate_distance(self, coord1: Coordinate, coord2: Coordinate) -> float:
        """Calculate approximate distance between two coordinates (in meters)"""
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(
            radians,
            [coord1.longitude, coord1.latitude, coord2.longitude, coord2.latitude]
        )
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        return 6371000 * c  # Earth radius in meters


# Global brain instance
brain = UrbanFlowBrain()

