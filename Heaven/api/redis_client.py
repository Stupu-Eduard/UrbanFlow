"""
Redis client for real-time data access
Reads data from AI Vision (Role 1)
"""
import redis
import json
from typing import Dict, List, Optional
from config import settings
from contracts import RedisKeys, ParkingStatus, EmergencyVehicleData


class RedisClient:
    """Client for accessing real-time data from Redis"""
    
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    
    def ping(self) -> bool:
        """Check if Redis is available"""
        try:
            return self.client.ping()
        except Exception:
            return False
    
    # ========================================
    # Traffic Data Access
    # ========================================
    
    def get_traffic_congestion(self, street_name: str) -> Optional[float]:
        """
        Get congestion score for a specific street
        Returns: Float 0.0 to 1.0, or None if not available
        
        Vision Engine Format: "urbanflow:traffic:{street_name}" = "0.75"
        """
        key = RedisKeys.traffic(street_name)
        value = self.client.get(key)
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        return None
    
    def get_all_traffic_data(self) -> Dict[str, float]:
        """
        Get all traffic congestion data
        Returns: Dict of {street_name: congestion_score}
        
        Vision Engine Format: "urbanflow:traffic:street_1" = "0.75"
        """
        pattern = RedisKeys.all_traffic_pattern()
        keys = self.client.keys(pattern)
        
        result = {}
        for key in keys:
            # Extract street name from "urbanflow:traffic:street_1"
            street_name = key.split(":")[-1]
            value = self.client.get(key)
            if value is not None:
                try:
                    result[street_name] = float(value)
                except (ValueError, TypeError):
                    continue
        
        return result
    
    def set_traffic_congestion(self, street_name: str, congestion: float):
        """
        Set traffic congestion (for testing - normally set by Role 1)
        
        Vision Engine Format: "urbanflow:traffic:{street_name}" = "0.75"
        """
        key = RedisKeys.traffic(street_name)
        self.client.set(key, str(congestion))
    
    # ========================================
    # Parking Data Access
    # ========================================
    
    def get_parking_status(self, spot_name: str) -> Optional[ParkingStatus]:
        """
        Get parking spot status
        Returns: ParkingStatus enum or None
        
        Vision Engine Format: "urbanflow:parking:SPOT_A1" = "free" or "occupied"
        """
        key = RedisKeys.parking(spot_name)
        value = self.client.get(key)
        if value:
            try:
                return ParkingStatus(value.lower())
            except ValueError:
                return ParkingStatus.UNKNOWN
        return None
    
    def get_all_parking_data(self) -> Dict[str, ParkingStatus]:
        """
        Get all parking spot statuses
        Returns: Dict of {spot_name: ParkingStatus}
        
        Vision Engine Format: "urbanflow:parking:SPOT_A1" = "free"
        """
        pattern = RedisKeys.all_parking_pattern()
        keys = self.client.keys(pattern)
        
        result = {}
        for key in keys:
            # Extract spot name from "urbanflow:parking:SPOT_A1"
            spot_name = key.split(":")[-1]
            value = self.client.get(key)
            if value:
                try:
                    result[spot_name] = ParkingStatus(value.lower())
                except ValueError:
                    result[spot_name] = ParkingStatus.UNKNOWN
        
        return result
    
    def set_parking_status(self, spot_name: str, status: ParkingStatus):
        """
        Set parking status (for testing - normally set by Role 1)
        
        Vision Engine Format: "urbanflow:parking:SPOT_A1" = "free"
        """
        key = RedisKeys.parking(spot_name)
        self.client.set(key, status.value)
    
    # ========================================
    # Emergency Vehicle Data Access
    # ========================================
    
    def get_emergency_vehicle(self, vehicle_id: str) -> Optional[EmergencyVehicleData]:
        """
        Get emergency vehicle real-time data
        Returns: EmergencyVehicleData or None
        
        Vision Engine Format:
        "urbanflow:emergency:truck_01" = {
            "id": "truck_01",
            "location": [640, 320],
            "bbox": [600, 280, 680, 360],
            "timestamp": 1234567890.123
        }
        TTL: 5 seconds
        """
        key = RedisKeys.emergency(vehicle_id)
        value = self.client.get(key)
        if value:
            try:
                data = json.loads(value)
                return EmergencyVehicleData(**data)
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                print(f"Error parsing emergency vehicle data: {e}")
                return None
        return None
    
    def get_all_emergency_vehicles(self) -> List[EmergencyVehicleData]:
        """
        Get all emergency vehicle data
        Returns: List of EmergencyVehicleData
        
        Vision Engine provides: urbanflow:emergency:truck_* with 5s TTL
        """
        pattern = RedisKeys.all_emergency_pattern()
        keys = self.client.keys(pattern)
        
        result = []
        for key in keys:
            value = self.client.get(key)
            if value:
                try:
                    data = json.loads(value)
                    result.append(EmergencyVehicleData(**data))
                except (json.JSONDecodeError, TypeError, ValueError):
                    continue
        
        return result
    
    def set_emergency_vehicle(self, data: EmergencyVehicleData, ttl: int = 5):
        """
        Set emergency vehicle data (for testing - normally set by Role 1)
        
        Vision Engine Format with TTL of 5 seconds
        """
        key = RedisKeys.emergency(data.id)
        self.client.setex(key, ttl, data.model_dump_json())
    
    # ========================================
    # Utility Methods
    # ========================================
    
    def clear_all_data(self):
        """Clear all UrbanFlow data (for testing)"""
        patterns = [
            RedisKeys.all_traffic_pattern(),
            RedisKeys.all_parking_pattern(),
            RedisKeys.all_emergency_pattern()
        ]
        
        for pattern in patterns:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)


# Global Redis client instance
redis_client = RedisClient()

