"""
Database models and connection management for PostgreSQL
"""
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from geoalchemy2 import Geometry
from datetime import datetime
from config import settings

# SQLAlchemy base
Base = declarative_base()

# Database engine
engine = create_engine(settings.database_url, echo=False)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ========================================
# Database Models
# ========================================

class StreetSegmentDB(Base):
    """Street segment stored in database"""
    __tablename__ = "street_segments"
    
    street_id = Column(String, primary_key=True)
    street_name = Column(String, nullable=False)
    geometry = Column(Geometry('LINESTRING', srid=4326), nullable=False)
    max_speed = Column(Float)  # km/h
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ParkingZoneDB(Base):
    """Parking zone stored in database"""
    __tablename__ = "parking_zones"
    
    zone_id = Column(String, primary_key=True)
    zone_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    total_capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ParkingSpotDB(Base):
    """Individual parking spot stored in database"""
    __tablename__ = "parking_spots"
    
    spot_id = Column(String, primary_key=True)
    zone_id = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmergencyVehicleDB(Base):
    """Emergency vehicle registry"""
    __tablename__ = "emergency_vehicles"
    
    vehicle_id = Column(String, primary_key=True)
    vehicle_type = Column(String, nullable=False)  # ambulance, fire_truck, police
    license_plate = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ========================================
# Database Utilities
# ========================================

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session (for dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_sample_data(db: Session):
    """Seed database with sample data for testing"""
    
    # Sample streets
    streets = [
        StreetSegmentDB(
            street_id="street_1",
            street_name="Main Street",
            geometry="SRID=4326;LINESTRING(-73.9857 40.7484, -73.9847 40.7494)",
            max_speed=50
        ),
        StreetSegmentDB(
            street_id="street_2",
            street_name="Broadway",
            geometry="SRID=4326;LINESTRING(-73.9847 40.7494, -73.9837 40.7504)",
            max_speed=40
        ),
        StreetSegmentDB(
            street_id="street_3",
            street_name="Park Avenue",
            geometry="SRID=4326;LINESTRING(-73.9837 40.7504, -73.9827 40.7514)",
            max_speed=60
        ),
    ]
    
    # Sample parking zones
    zones = [
        ParkingZoneDB(
            zone_id="zone_A",
            zone_name="Central Parking",
            latitude=40.7489,
            longitude=-73.9852,
            total_capacity=50
        ),
        ParkingZoneDB(
            zone_id="zone_B",
            zone_name="North Plaza",
            latitude=40.7499,
            longitude=-73.9842,
            total_capacity=30
        ),
    ]
    
    # Sample parking spots (matching Vision Engine format: SPOT_A1, SPOT_A2, etc.)
    spots = []
    for i in range(1, 51):
        spots.append(ParkingSpotDB(
            spot_id=f"SPOT_A{i}",  # Vision Engine format
            zone_id="zone_A",
            latitude=40.7489 + (i * 0.0001),
            longitude=-73.9852 + (i * 0.0001)
        ))
    
    for i in range(1, 31):
        spots.append(ParkingSpotDB(
            spot_id=f"SPOT_B{i}",  # Vision Engine format
            zone_id="zone_B",
            latitude=40.7499 + (i * 0.0001),
            longitude=-73.9842 + (i * 0.0001)
        ))
    
    # Sample emergency vehicles (matching Vision Engine format: truck_01, etc.)
    vehicles = [
        EmergencyVehicleDB(
            vehicle_id="truck_01",  # Vision Engine format
            vehicle_type="ambulance",
            license_plate="EMG-001"
        ),
        EmergencyVehicleDB(
            vehicle_id="truck_02",  # Vision Engine format
            vehicle_type="fire_truck",
            license_plate="FIRE-001"
        ),
    ]
    
    # Add all to database
    try:
        db.add_all(streets + zones + spots + vehicles)
        db.commit()
        print("✓ Sample data seeded successfully")
    except Exception as e:
        print(f"✗ Error seeding data: {e}")
        db.rollback()

