"""
UrbanFlowAI - The Brain (Main API)
FastAPI application that serves as the central backend
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
from contextlib import asynccontextmanager

from config import settings
from database import get_db, init_db, engine
from contracts import LiveStatusResponse, RouteRequest, RouteResponse
from services import brain
from redis_client import redis_client

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info("🚀 Starting UrbanFlowAI - The Brain")
    logger.info("Initializing database...")
    init_db()
    logger.info("✓ Database initialized")
    
    # Check Redis connection
    if redis_client.ping():
        logger.info("✓ Redis connection established")
    else:
        logger.warning("⚠ Redis connection failed - real-time data may be unavailable")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down UrbanFlowAI")


# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# Health Check Endpoints
# ========================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information"""
    return {
        "service": "UrbanFlowAI - The Brain",
        "version": settings.API_VERSION,
        "status": "operational",
        "description": "Central backend API for intelligent city traffic management"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    redis_status = redis_client.ping()
    
    # Check database
    db_status = False
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    return {
        "status": "healthy" if (redis_status and db_status) else "degraded",
        "services": {
            "redis": "connected" if redis_status else "disconnected",
            "database": "connected" if db_status else "disconnected"
        }
    }


# ========================================
# CORE API: Function 1 - Live Status
# ========================================

@app.get("/api/v1/status/live", response_model=LiveStatusResponse, tags=["Live Status"])
async def get_live_status(db: Session = Depends(get_db)):
    """
    **Live Status Function** - Get real-time snapshot of the entire city
    
    This endpoint provides:
    - Real-time traffic congestion for all streets
    - Parking availability across all zones
    - Active emergency vehicle locations
    - City-wide statistics
    
    **For Role 3 (Frontend):** This is your primary data source for the dashboard.
    Call this endpoint periodically (e.g., every 5-10 seconds) to update the live view.
    """
    try:
        return await brain.get_live_status(db)
    except Exception as e:
        logger.error(f"Error getting live status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve live status: {str(e)}"
        )


# ========================================
# CORE API: Function 2 - Route Calculation
# ========================================

@app.post("/api/v1/route/calculate", response_model=RouteResponse, tags=["Routing"])
async def calculate_route(
    request: RouteRequest,
    db: Session = Depends(get_db)
):
    """
    **Route Calculation Function** - Calculate intelligent routes based on mode
    
    **Modes:**
    - `citizen`: Fast standard routing for regular drivers
    - `emergency`: Priority routing that avoids congested streets
    - `smartpark`: Navigation to nearest available parking spot
    
    **For Role 3 (Frontend):** 
    - For citizen navigation, use mode "citizen"
    - For ambulance/emergency vehicles, use mode "emergency" with vehicle_id
    - For parking assistance, use mode "smartpark"
    
    The response includes:
    - Complete route with coordinates for map display
    - Turn-by-turn instructions
    - Distance and duration estimates
    - (Emergency mode only) List of congested streets avoided
    """
    try:
        # Validate emergency mode requirements
        if request.mode == "emergency" and not request.vehicle_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="vehicle_id is required for emergency mode"
            )
        
        return await brain.calculate_route(request, db)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error calculating route: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate route: {str(e)}"
        )


# ========================================
# Admin/Testing Endpoints
# ========================================

@app.post("/api/v1/admin/seed-data", tags=["Admin"])
async def seed_database(db: Session = Depends(get_db)):
    """
    Seed database with sample data for testing
    
    **Warning:** This will add sample streets, parking zones, and vehicles
    """
    from database import seed_sample_data
    try:
        seed_sample_data(db)
        return {"message": "Database seeded successfully"}
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed database: {str(e)}"
        )


@app.post("/api/v1/admin/seed-redis", tags=["Admin"])
async def seed_redis_data():
    """
    Seed Redis with sample real-time data for testing
    
    **Matches Vision Engine Format:**
    - Traffic: urbanflow:traffic:{street_name} = "0.75"
    - Parking: urbanflow:parking:{spot_name} = "free"
    - Emergency: urbanflow:emergency:truck_{id} = {...}
    """
    try:
        from contracts import EmergencyVehicleData, ParkingStatus
        import time
        
        # Sample traffic data (Vision Engine format)
        redis_client.set_traffic_congestion("street_1", 0.3)  # Low
        redis_client.set_traffic_congestion("street_2", 0.6)  # Medium
        redis_client.set_traffic_congestion("street_3", 0.9)  # High
        
        # Sample parking data (Vision Engine format: SPOT_A1, SPOT_A2, etc.)
        for i in range(1, 51):
            status = ParkingStatus.FREE if i % 3 != 0 else ParkingStatus.OCCUPIED
            redis_client.set_parking_status(f"SPOT_A{i}", status)
        
        for i in range(1, 31):
            status = ParkingStatus.FREE if i % 2 == 0 else ParkingStatus.OCCUPIED
            redis_client.set_parking_status(f"SPOT_B{i}", status)
        
        # Sample emergency vehicle (Vision Engine format)
        redis_client.set_emergency_vehicle(EmergencyVehicleData(
            id="truck_01",
            location=[640.0, 320.0],  # Pixel coordinates
            bbox=[600.0, 280.0, 680.0, 360.0],  # Bounding box
            timestamp=time.time(),
            # Optional fields for conversion
            latitude=40.7489,
            longitude=-73.9852,
            status="responding"
        ), ttl=5)  # 5 second TTL as per Vision Engine
        
        return {
            "message": "Redis seeded with sample data (Vision Engine format)",
            "format": {
                "traffic": "urbanflow:traffic:{street_name} = float",
                "parking": "urbanflow:parking:{spot_name} = 'free'|'occupied'",
                "emergency": "urbanflow:emergency:truck_{id} = JSON (TTL: 5s)"
            },
            "data": {
                "streets": 3,
                "parking_spots": 80,
                "emergency_vehicles": 1
            }
        }
        
    except Exception as e:
        logger.error(f"Error seeding Redis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed Redis: {str(e)}"
        )


@app.get("/api/v1/admin/redis-status", tags=["Admin"])
async def get_redis_status():
    """
    Get current Redis data for debugging
    """
    try:
        traffic = redis_client.get_all_traffic_data()
        parking = redis_client.get_all_parking_data()
        emergency = redis_client.get_all_emergency_vehicles()
        
        return {
            "traffic_segments": len(traffic),
            "parking_spots": len(parking),
            "emergency_vehicles": len(emergency),
            "sample_traffic": dict(list(traffic.items())[:5]),
            "sample_parking": dict(list(parking.items())[:5])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Redis status: {str(e)}"
        )


# ========================================
# Run the application
# ========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )

