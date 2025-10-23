# 🚀 UrbanFlowAI Setup Guide

**Step-by-step guide to get UrbanFlowAI running**

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Starting Services](#starting-services)
5. [Database Initialization](#database-initialization)
6. [Map Data Setup](#map-data-setup)
7. [Testing](#testing)
8. [Next Steps](#next-steps)

---

## Prerequisites

### Required Software
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
  - Download: https://www.docker.com/products/docker-desktop
  - Minimum version: 20.10+
  
- **Docker Compose**
  - Included with Docker Desktop
  - Linux: `sudo apt-get install docker-compose`

- **Git**
  - Download: https://git-scm.com/downloads

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 5GB minimum (10GB+ with full map data)
- **OS**: Windows 10+, macOS 10.14+, or Linux

### Optional (for local development)
- Python 3.11+
- PostgreSQL client tools
- Redis CLI

---

## Installation

### Step 1: Get the Code

```bash
# Clone the repository (or extract from zip)
git clone <repository-url>
cd UrbanFlowAI

# Or if you have a zip file:
unzip UrbanFlowAI.zip
cd UrbanFlowAI
```

### Step 2: Verify File Structure

Your directory should look like this:
```
UrbanFlowAI/
├── docker-compose.yml
├── api/
│   ├── Dockerfile
│   ├── main.py
│   ├── config.py
│   ├── contracts.py
│   ├── database.py
│   ├── redis_client.py
│   ├── routing_service.py
│   ├── services.py
│   └── requirements.txt
├── init-db/
│   └── 01-init.sql
├── README.md
└── SETUP_GUIDE.md
```

---

## Configuration

### Step 1: Environment Variables

The default configuration works out-of-the-box for development. If you need to customize:

**Windows (PowerShell):**
```powershell
# Set environment variables
$env:REDIS_HOST = "redis"
$env:POSTGRES_HOST = "postgres"
```

**Linux/Mac:**
```bash
# Edit docker-compose.yml to change default settings
# All settings are in the 'environment' section of each service
```

### Step 2: Port Availability

Ensure these ports are free:
- 8000 (API)
- 6379 (Redis)
- 5432 (PostgreSQL)
- 5000 (OSRM)
- 8989 (GraphHopper)

**Check port availability:**

Windows:
```powershell
netstat -ano | findstr "8000"
```

Linux/Mac:
```bash
lsof -i :8000
```

---

## Starting Services

### Step 1: Build and Start

```bash
# Build and start all services
docker-compose up -d

# This will:
# - Pull required Docker images
# - Build the API container
# - Start Redis, PostgreSQL, OSRM, GraphHopper, and API
# - Create networks and volumes
```

**First-time startup takes 3-5 minutes.** Wait for all services to be healthy.

### Step 2: Verify Services

```bash
# Check service status
docker-compose ps

# All services should show "Up" or "Up (healthy)"
```

Expected output:
```
NAME                    STATUS              PORTS
urbanflow-api           Up (healthy)        0.0.0.0:8000->8000/tcp
urbanflow-redis         Up (healthy)        0.0.0.0:6379->6379/tcp
urbanflow-postgres      Up (healthy)        0.0.0.0:5432->5432/tcp
urbanflow-osrm          Up (healthy)        0.0.0.0:5000->5000/tcp
urbanflow-graphhopper   Up (healthy)        0.0.0.0:8989->8989/tcp
```

### Step 3: Check Logs

```bash
# View all logs
docker-compose logs

# Follow API logs
docker-compose logs -f api

# You should see:
# ✓ Database initialized
# ✓ Redis connection established
```

---

## Database Initialization

### Step 1: Initialize PostgreSQL

The database is automatically initialized via `init-db/01-init.sql`.

Verify it worked:
```bash
docker-compose exec postgres psql -U urbanflow -d urbanflow -c "SELECT PostGIS_version();"
```

### Step 2: Seed Sample Data

Populate the database with sample streets, parking zones, and vehicles:

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/v1/admin/seed-data -Method POST
```

**Linux/Mac/Git Bash:**
```bash
curl -X POST http://localhost:8000/api/v1/admin/seed-data
```

Expected response:
```json
{"message": "Database seeded successfully"}
```

### Step 3: Seed Redis with Sample Data

Add sample real-time traffic and parking data:

```bash
curl -X POST http://localhost:8000/api/v1/admin/seed-redis
```

Expected response:
```json
{
  "message": "Redis seeded with sample data",
  "data": {
    "streets": 3,
    "parking_spots": 80,
    "emergency_vehicles": 1
  }
}
```

---

## Map Data Setup

**Note:** OSRM and GraphHopper need map data to provide routing. For quick testing, you can skip this and use the API in "demo mode" (it will return fallback routes).

### Option 1: Quick Demo (Monaco - Small Dataset)

**Windows (PowerShell):**
```powershell
# Create directories
New-Item -ItemType Directory -Path "osrm-data" -Force
New-Item -ItemType Directory -Path "graphhopper-data" -Force

# Download small map
Invoke-WebRequest -Uri "http://download.geofabrik.de/europe/monaco-latest.osm.pbf" -OutFile "osrm-data\map.osm.pbf"

# Process for OSRM (this takes 2-3 minutes)
docker run -t -v "${PWD}/osrm-data:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/map.osm.pbf
docker run -t -v "${PWD}/osrm-data:/data" osrm/osrm-backend osrm-partition /data/map.osrm
docker run -t -v "${PWD}/osrm-data:/data" osrm/osrm-backend osrm-customize /data/map.osrm

# Copy for GraphHopper
Copy-Item "osrm-data\map.osm.pbf" "graphhopper-data\map.osm.pbf"

# Restart routing services
docker-compose restart osrm graphhopper
```

**Linux/Mac:**
```bash
# Create directories
mkdir -p osrm-data graphhopper-data

# Download small map
wget http://download.geofabrik.de/europe/monaco-latest.osm.pbf \
  -O osrm-data/map.osm.pbf

# Process for OSRM
docker run -t -v "${PWD}/osrm-data:/data" osrm/osrm-backend \
  osrm-extract -p /opt/car.lua /data/map.osm.pbf

docker run -t -v "${PWD}/osrm-data:/data" osrm/osrm-backend \
  osrm-partition /data/map.osrm

docker run -t -v "${PWD}/osrm-data:/data" osrm/osrm-backend \
  osrm-customize /data/map.osrm

# Copy for GraphHopper
cp osrm-data/map.osm.pbf graphhopper-data/

# Restart
docker-compose restart osrm graphhopper
```

### Option 2: Your City's Map Data

1. **Download your region** from [Geofabrik](http://download.geofabrik.de/)
   - Example: For New York: `us/new-york-latest.osm.pbf`

2. **Process as shown above**, replacing `monaco-latest.osm.pbf` with your file

3. **Larger maps take longer** to process:
   - City: 5-10 minutes
   - State: 30-60 minutes
   - Country: hours

---

## Testing

### Step 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "redis": "connected",
    "database": "connected"
  }
}
```

### Step 2: Get Live Status

```bash
curl http://localhost:8000/api/v1/status/live
```

You should see JSON with streets, parking, and emergency data.

### Step 3: Calculate a Route (Citizen Mode)

```bash
curl -X POST http://localhost:8000/api/v1/route/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"latitude": 40.7489, "longitude": -73.9852},
    "end": {"latitude": 40.7599, "longitude": -73.9762},
    "mode": "citizen"
  }'
```

### Step 4: Calculate Emergency Route

```bash
curl -X POST http://localhost:8000/api/v1/route/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"latitude": 40.7489, "longitude": -73.9852},
    "end": {"latitude": 40.7599, "longitude": -73.9762},
    "mode": "emergency",
    "vehicle_id": "amb_001"
  }'
```

### Step 5: Browse API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Next Steps

### For Role 1 (AI Vision Engineer)

You need to populate Redis with real-time data. See examples:

**Python Example:**
```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Traffic data
r.set('traffic:street_1', '0.75')

# Parking data
r.set('parking:zone_A:A1', 'free')

# Emergency vehicle
vehicle = {
    "vehicle_id": "amb_001",
    "latitude": 40.7489,
    "longitude": -73.9852,
    "status": "responding",
    "last_updated": "2024-01-15T10:30:00Z"
}
r.set('emergency:amb_001', json.dumps(vehicle))
```

### For Role 3 (Frontend Engineer)

Consume the API:

**JavaScript Example:**
```javascript
// Get live status
const response = await fetch('http://localhost:8000/api/v1/status/live');
const data = await response.json();

console.log('Streets:', data.streets);
console.log('Parking:', data.parking_zones);
console.log('Emergency:', data.emergency_vehicles);

// Calculate route
const routeResponse = await fetch('http://localhost:8000/api/v1/route/calculate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    start: {latitude: 40.7489, longitude: -73.9852},
    end: {latitude: 40.7599, longitude: -73.9762},
    mode: 'citizen'
  })
});

const route = await routeResponse.json();
console.log('Route:', route);
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker version

# Check logs for errors
docker-compose logs

# Restart everything
docker-compose down
docker-compose up -d
```

### Port Already in Use

```bash
# Stop conflicting services or change ports in docker-compose.yml
# Example: Change API port from 8000 to 8001
ports:
  - "8001:8000"
```

### Redis/Database Connection Errors

```bash
# Restart specific service
docker-compose restart redis
docker-compose restart postgres

# Check service logs
docker-compose logs redis
docker-compose logs postgres
```

### OSRM/GraphHopper Errors

- These services need processed map data to work
- Without map data, the API falls back to simple routing
- Follow "Map Data Setup" section above

---

## Clean Restart

If something goes wrong, reset everything:

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

---

## Getting Help

1. **Check logs**: `docker-compose logs -f`
2. **API documentation**: http://localhost:8000/docs
3. **Health status**: http://localhost:8000/health
4. **Redis status**: http://localhost:8000/api/v1/admin/redis-status

---

**You're all set! The Brain is now operational.** 🧠✨

