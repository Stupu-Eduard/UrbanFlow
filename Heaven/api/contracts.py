"""
Data Contracts for UrbanFlowAI
Defines the "language" between Role 1 (AI Vision), Role 2 (Backend), and Role 3 (Frontend)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


# ========================================
# INPUT CONTRACT (from Role 1: AI Vision)
# ========================================

class RedisKeys:
    """
    Redis key naming convention for real-time data from AI Vision (Role 1)
    
    ACTUAL FORMAT FROM VISION ENGINE:
    - Traffic: "urbanflow:traffic:{street_name}" -> congestion score (0.0 to 1.0)
    - Parking: "urbanflow:parking:{spot_name}" -> status ("free" or "occupied")
    - Emergency: "urbanflow:emergency:truck_{id}" -> JSON with location and bbox
    """
    
    @staticmethod
    def traffic(street_name: str) -> str:
        """Get Redis key for street traffic congestion"""
        return f"urbanflow:traffic:{street_name}"
    
    @staticmethod
    def parking(spot_name: str) -> str:
        """Get Redis key for parking spot status"""
        return f"urbanflow:parking:{spot_name}"
    
    @staticmethod
    def emergency(vehicle_id: str) -> str:
        """Get Redis key for emergency vehicle location"""
        return f"urbanflow:emergency:{vehicle_id}"
    
    @staticmethod
    def all_traffic_pattern() -> str:
        """Pattern to get all traffic keys"""
        return "urbanflow:traffic:*"
    
    @staticmethod
    def all_parking_pattern() -> str:
        """Pattern to get all parking keys"""
        return "urbanflow:parking:*"
    
    @staticmethod
    def all_emergency_pattern() -> str:
        """Pattern to get all emergency vehicle keys"""
        return "urbanflow:emergency:truck_*"


class ParkingStatus(str, Enum):
    """Parking spot status from AI Vision"""
    FREE = "free"
    OCCUPIED = "occupied"
    UNKNOWN = "unknown"


class EmergencyVehicleData(BaseModel):
    """
    Emergency vehicle real-time data from AI Vision
    
    ACTUAL FORMAT FROM VISION ENGINE:
    {
      "id": "truck_01",
      "location": [x, y],  # Pixel coordinates
      "bbox": [x1, y1, x2, y2],  # Bounding box
      "timestamp": 1234567890.123
    }
    """
    id: str
    location: List[float]  # [x, y] pixel coordinates
    bbox: List[float]  # [x1, y1, x2, y2] bounding box
    timestamp: float
    
    # Additional fields for internal use (converted from pixel to geo coords)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None
    status: Literal["active", "idle", "responding"] = "active"


# ========================================
# OUTPUT CONTRACT (to Role 3: Frontend)
# ========================================

class CongestionLevel(str, Enum):
    """Human-readable congestion level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StreetStatus(BaseModel):
    """Traffic status for a single street"""
    street_id: str
    street_name: str
    congestion_score: float = Field(..., ge=0.0, le=1.0, description="0.0 = free flowing, 1.0 = gridlock")
    congestion_level: CongestionLevel
    coordinates: List[List[float]]  # [[lon, lat], [lon, lat], ...]


class ParkingSpotStatus(BaseModel):
    """Status for a single parking spot"""
    spot_id: str
    zone_id: str
    zone_name: str
    status: ParkingStatus
    latitude: float
    longitude: float


class ParkingZoneSummary(BaseModel):
    """Aggregated parking zone information"""
    zone_id: str
    zone_name: str
    total_spots: int
    free_spots: int
    occupancy_rate: float = Field(..., ge=0.0, le=1.0)
    latitude: float
    longitude: float


class EmergencyVehicleStatus(BaseModel):
    """Emergency vehicle status for frontend"""
    vehicle_id: str
    vehicle_type: str  # "ambulance", "fire_truck", "police"
    latitude: float
    longitude: float
    heading: Optional[float] = None
    speed: Optional[float] = None
    status: str
    last_updated: datetime


class LiveStatusResponse(BaseModel):
    """
    Complete real-time city status - Response for "Live Status" function
    This is the main snapshot that the frontend dashboard will display
    """
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Traffic information
    streets: List[StreetStatus]
    average_congestion: float = Field(..., ge=0.0, le=1.0)
    
    # Parking information
    parking_zones: List[ParkingZoneSummary]
    total_parking_spots: int
    total_free_spots: int
    
    # Emergency vehicles
    emergency_vehicles: List[EmergencyVehicleStatus]
    active_emergencies: int


# ========================================
# ROUTING CONTRACT (Input/Output)
# ========================================

class RoutingMode(str, Enum):
    """Routing mode selection"""
    CITIZEN = "citizen"  # Standard fast routing (OSRM)
    EMERGENCY = "emergency"  # Priority routing avoiding congestion (GraphHopper)
    SMARTPARK = "smartpark"  # Navigation to nearest free parking


class Coordinate(BaseModel):
    """GPS coordinate"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class RouteRequest(BaseModel):
    """Request for route calculation"""
    start: Coordinate
    end: Coordinate
    mode: RoutingMode
    vehicle_id: Optional[str] = None  # Required for emergency mode


class RouteStep(BaseModel):
    """Single step in a route"""
    instruction: str
    distance: float  # meters
    duration: float  # seconds
    coordinates: List[List[float]]  # [[lon, lat], ...]


class RouteResponse(BaseModel):
    """Response with calculated route"""
    mode: RoutingMode
    start: Coordinate
    end: Coordinate
    
    # Route geometry (full path)
    coordinates: List[List[float]]  # [[lon, lat], ...]
    
    # Route metrics
    total_distance: float  # meters
    total_duration: float  # seconds
    
    # Detailed steps
    steps: List[RouteStep]
    
    # Metadata
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    avoided_congested_streets: Optional[List[str]] = None  # For emergency mode
    
    # Parking info (for smartpark mode)
    destination_parking_zone: Optional[str] = None
    available_spots_at_destination: Optional[int] = None


# ========================================
# INTERNAL MODELS (Database)
# ========================================

class StreetSegment(BaseModel):
    """Street segment definition (stored in PostgreSQL)"""
    street_id: str
    street_name: str
    geometry: str  # WKT LineString
    max_speed: Optional[float] = None  # km/h


class ParkingZone(BaseModel):
    """Parking zone definition (stored in PostgreSQL)"""
    zone_id: str
    zone_name: str
    latitude: float
    longitude: float
    total_capacity: int


class ParkingSpot(BaseModel):
    """Individual parking spot (stored in PostgreSQL)"""
    spot_id: str
    zone_id: str
    latitude: float
    longitude: float

