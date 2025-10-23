# 🧠 UrbanFlowAI - The Brain

**Central Backend API for Intelligent City Traffic Management**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com)

## 🎯 Project Vision

UrbanFlowAI is an intelligent "conductor" for city traffic, managing three key city services:

- 🚑 **Emergency Mode**: Creating priority routes for ambulances
- 🚗 **Citizen Mode**: Smart navigation that prevents traffic jams
- 🅿️ **SmartPark Mode**: Guiding drivers to real-time parking spots

## 🏗️ Architecture Overview

```
┌─────────────────┐
│   Role 1: AI    │  → Watches city via video feeds
│  Vision (Eyes)  │  → Produces real-time facts
└────────┬────────┘
         │ Redis (Real-time DB)
         ▼
┌─────────────────┐
│   Role 2: The   │  ← YOU ARE HERE
│   Brain (API)   │  → Central intelligence & routing
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐
│   Role 3: The   │  → Visual dashboard & app
│   Face (UI)     │  → User interface
└─────────────────┘
```

## 🔧 Technology Stack

### Infrastructure
- **FastAPI**: Modern, fast Python web framework
- **Redis**: Real-time in-memory database for live data
- **PostgreSQL + PostGIS**: Persistent database for city map data
- **OSRM**: Ultra-fast routing engine (Citizen Mode)
- **GraphHopper**: Flexible routing engine (Emergency Mode)
- **Docker Compose**: Orchestration for all services

### Key Libraries
- **SQLAlchemy + GeoAlchemy2**: Database ORM with geospatial support
- **Pydantic**: Data validation and settings management
- **httpx**: Async HTTP client for routing engines

## 📋 Data Contracts

### INPUT: From Role 1 (AI Vision) → Redis

**Traffic Congestion:**
```
Key: "urbanflow:traffic:{street_name}"
Value: "0.75"  (float 0.0 to 1.0)
```

**Parking Status:**
```
Key: "urbanflow:parking:{spot_name}"
Value: "free" | "occupied"
Example: "urbanflow:parking:SPOT_A1" = "free"
```

**Emergency Vehicles:**
```
Key: "urbanflow:emergency:truck_{id}"
Value: {
  "id": "truck_01",
  "location": [640.0, 320.0],
  "bbox": [600, 280, 680, 360],
  "timestamp": 1234567890.123,
  "latitude": 40.7489,
  "longitude": -73.9852,
  "status": "responding"
}
TTL: 5 seconds
```

### OUTPUT: To Role 3 (Frontend) → REST API

**Endpoint 1: Live Status**
```http
GET /api/v1/status/live
```

Response:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "streets": [
    {
      "street_id": "street_1",
      "street_name": "Main Street",
      "congestion_score": 0.3,
      "congestion_level": "low",
      "coordinates": [[lon, lat], ...]
    }
  ],
  "average_congestion": 0.45,
  "parking_zones": [
    {
      "zone_id": "zone_A",
      "zone_name": "Central Parking",
      "total_spots": 50,
      "free_spots": 23,
      "occupancy_rate": 0.54,
      "latitude": 40.7489,
      "longitude": -73.9852
    }
  ],
  "total_parking_spots": 80,
  "total_free_spots": 35,
  "emergency_vehicles": [...],
  "active_emergencies": 1
}
```

**Endpoint 2: Route Calculation**
```http
POST /api/v1/route/calculate
Content-Type: application/json

{
  "start": {"latitude": 40.7489, "longitude": -73.9852},
  "end": {"latitude": 40.7599, "longitude": -73.9762},
  "mode": "citizen" | "emergency" | "smartpark",
  "vehicle_id": "amb_001"  // Required for emergency mode
}
```

Response:
```json
{
  "mode": "emergency",
  "start": {...},
  "end": {...},
  "coordinates": [[lon, lat], ...],
  "total_distance": 2500.5,
  "total_duration": 180.0,
  "steps": [
    {
      "instruction": "Turn left onto Main St",
      "distance": 500,
      "duration": 30,
      "coordinates": [...]
    }
  ],
  "avoided_congested_streets": ["street_2", "street_5"]
}
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- (Optional) Python 3.11+ for local development

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd UrbanFlowAI

# Copy environment configuration
cp .env.example .env

# Edit .env if needed (default values work for development)
```

### 2. Start Infrastructure

```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f api
```

### 3. Initialize Database

```bash
# Seed database with sample data
curl -X POST http://localhost:8000/api/v1/admin/seed-data

# Seed Redis with sample real-time data
curl -X POST http://localhost:8000/api/v1/admin/seed-redis
```

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Get live status
curl http://localhost:8000/api/v1/status/live

# Calculate a route
curl -X POST http://localhost:8000/api/v1/route/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"latitude": 40.7489, "longitude": -73.9852},
    "end": {"latitude": 40.7599, "longitude": -73.9762},
    "mode": "citizen"
  }'
```

### 5. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📦 Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| API (FastAPI) | 8000 | Main backend API |
| Redis | 6379 | Real-time data store |
| PostgreSQL | 5432 | Persistent database |
| OSRM | 5000 | Fast routing (Citizen) |
| GraphHopper | 8989 | Smart routing (Emergency) |

## 🗺️ Map Data Setup (OSRM & GraphHopper)

**Note**: OSRM and GraphHopper require pre-processed map data to function.

### Quick Setup (Sample Data)

For development/testing, you can use a small map extract:

```bash
# Create data directories
mkdir -p osrm-data graphhopper-data

# Download a small map extract (e.g., Monaco)
wget http://download.geofabrik.de/europe/monaco-latest.osm.pbf \
  -O osrm-data/map.osm.pbf

# Process for OSRM
docker run -t -v "${PWD}/osrm-data:/data" osrm/osrm-backend \
  osrm-extract -p /opt/car.lua /data/map.osm.pbf

docker run -t -v "${PWD}/osrm-data:/data" osrm/osrm-backend \
  osrm-partition /data/map.osrm

docker run -t -v "${PWD}/osrm-data:/data" osrm/osrm-backend \
  osrm-customize /data/map.osrm

# Copy map for GraphHopper
cp osrm-data/map.osm.pbf graphhopper-data/

# Now restart services
docker-compose restart osrm graphhopper
```

### Production Setup

For your actual city:
1. Download your region from [Geofabrik](http://download.geofabrik.de/)
2. Process with OSRM and GraphHopper as shown above
3. Update `docker-compose.yml` with correct map paths

## 🧪 Testing & Development

### Manual Testing with Sample Data

```bash
# 1. Seed databases
curl -X POST http://localhost:8000/api/v1/admin/seed-data
curl -X POST http://localhost:8000/api/v1/admin/seed-redis

# 2. Check Redis data
curl http://localhost:8000/api/v1/admin/redis-status

# 3. Get live status
curl http://localhost:8000/api/v1/status/live | jq

# 4. Test citizen routing
curl -X POST http://localhost:8000/api/v1/route/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"latitude": 40.7489, "longitude": -73.9852},
    "end": {"latitude": 40.7599, "longitude": -73.9762},
    "mode": "citizen"
  }' | jq

# 5. Test emergency routing
curl -X POST http://localhost:8000/api/v1/route/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"latitude": 40.7489, "longitude": -73.9852},
    "end": {"latitude": 40.7599, "longitude": -73.9762},
    "mode": "emergency",
    "vehicle_id": "amb_001"
  }' | jq
```

### Local Development (Without Docker)

```bash
# Install dependencies
cd api
pip install -r requirements.txt

# Start Redis and PostgreSQL (or use Docker for just these)
docker-compose up -d redis postgres

# Set environment variables
export REDIS_HOST=localhost
export POSTGRES_HOST=localhost
export OSRM_URL=http://localhost:5000
export GRAPHHOPPER_URL=http://localhost:8989

# Run the API
python main.py
```

## 📚 API Reference

### Core Endpoints

#### `GET /api/v1/status/live`
Get real-time city status snapshot.

**Response**: `LiveStatusResponse`
- Traffic congestion for all streets
- Parking availability by zone
- Emergency vehicle locations
- City-wide statistics

**Usage**: Call every 5-10 seconds for dashboard updates.

#### `POST /api/v1/route/calculate`
Calculate intelligent route based on mode.

**Request**: `RouteRequest`
- `start`: GPS coordinate
- `end`: GPS coordinate
- `mode`: "citizen" | "emergency" | "smartpark"
- `vehicle_id`: (Required for emergency mode)

**Response**: `RouteResponse`
- Full route with coordinates
- Turn-by-turn instructions
- Distance & duration
- Avoided streets (emergency mode)

### Admin Endpoints

#### `POST /api/v1/admin/seed-data`
Populate database with sample streets, parking zones, and vehicles.

#### `POST /api/v1/admin/seed-redis`
Populate Redis with sample real-time data for testing.

#### `GET /api/v1/admin/redis-status`
View current Redis data for debugging.

## 🔄 Integration Guide

### For Role 1 (AI Vision Engineer)

Your job is to populate Redis with real-time data:

**1. Traffic Data:**
```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Set congestion for a street (0.0 to 1.0)
r.set('urbanflow:traffic:street_1', '0.75')
```

**2. Parking Data:**
```python
# Mark spot as free or occupied (Vision Engine format)
r.set('urbanflow:parking:SPOT_A1', 'free')
r.set('urbanflow:parking:SPOT_A2', 'occupied')
```

**3. Emergency Vehicles:**
```python
import json
import time

vehicle_data = {
    "id": "truck_01",
    "location": [640.0, 320.0],  # Pixel coordinates from camera
    "bbox": [600.0, 280.0, 680.0, 360.0],
    "timestamp": time.time(),
    "latitude": 40.7489,  # Optional: converted GPS
    "longitude": -73.9852,
    "status": "responding"
}
# Set with 5 second TTL (Vision Engine format)
r.setex('urbanflow:emergency:truck_01', 5, json.dumps(vehicle_data))
```

### For Role 3 (Frontend Engineer)

Your job is to consume the REST API:

**1. Display Live Dashboard:**
```javascript
// Fetch live status every 10 seconds
async function updateDashboard() {
  const response = await fetch('http://localhost:8000/api/v1/status/live');
  const data = await response.json();
  
  // Update your UI with:
  // - data.streets (traffic map)
  // - data.parking_zones (parking availability)
  // - data.emergency_vehicles (ambulance locations)
}

setInterval(updateDashboard, 10000);
```

**2. Calculate Routes:**
```javascript
async function getRoute(start, end, mode) {
  const response = await fetch('http://localhost:8000/api/v1/route/calculate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      start: {latitude: start.lat, longitude: start.lng},
      end: {latitude: end.lat, longitude: end.lng},
      mode: mode  // 'citizen', 'emergency', or 'smartpark'
    })
  });
  
  const route = await response.json();
  // Display route.coordinates on map
  // Show route.steps for navigation
}
```

## 🐛 Troubleshooting

### Redis Connection Failed
```bash
# Check if Redis is running
docker-compose ps redis

# Check logs
docker-compose logs redis

# Restart Redis
docker-compose restart redis
```

### Database Connection Failed
```bash
# Check PostgreSQL
docker-compose ps postgres
docker-compose logs postgres

# Verify PostGIS
docker-compose exec postgres psql -U urbanflow -d urbanflow -c "SELECT PostGIS_version();"
```

### OSRM/GraphHopper Not Responding
- Ensure map data is properly processed (see "Map Data Setup")
- Check service logs: `docker-compose logs osrm` or `docker-compose logs graphhopper`
- Routing engines need time to start up (60-90 seconds)

### API Returns Empty Data
- Run seed commands to populate databases
- Check Redis has data: `curl http://localhost:8000/api/v1/admin/redis-status`

## 🔒 Security Notes

**For Production:**
1. Change default passwords in `.env`
2. Restrict CORS origins in `main.py`
3. Add authentication/API keys
4. Use HTTPS with reverse proxy (nginx)
5. Enable Redis authentication
6. Use PostgreSQL SSL connections

## 📈 Performance Tuning

- **Redis**: Increase memory limit for large cities
- **PostgreSQL**: Add indexes on frequently queried columns
- **API**: Increase Uvicorn workers: `--workers 4`
- **Caching**: Add Redis cache for routes
- **Rate Limiting**: Protect against API abuse

## 🤝 Contributing

This is Role 2 of a 3-role system. Coordinate with:
- **Role 1**: For Redis data format changes
- **Role 3**: For API contract modifications

## 📝 License

[Your License Here]

## 🆘 Support

For issues and questions:
- Check `/docs` endpoint for API documentation
- Review logs: `docker-compose logs -f`
- Test with admin endpoints: `/api/v1/admin/*`

---

**Built with ❤️ for smarter cities**

