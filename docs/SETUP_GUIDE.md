# 🚀 UrbanFlowAI - Complete Setup Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Backend Setup](#backend-setup)
4. [Vision Engine Setup](#vision-engine-setup)
5. [Integration](#integration)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- Python 3.13+
- Docker & Docker Compose
- CUDA-capable GPU (optional, for faster processing)
- Git

### 3-Step Startup

```bash
# 1. Start Backend
cd Heaven
docker-compose up -d

# 2. Start Vision Engine
cd ../VisionEngine
python scripts/detector.py

# 3. Access API
open http://localhost:8000/docs
```

---

## Installation

### 1. Install Python Dependencies

```bash
cd VisionEngine
pip install -r requirements.txt
```

### 2. Download YOLO Model

The model will download automatically on first run, or manually:

```bash
# Downloads yolo11x.pt (~110MB)
python -c "from ultralytics import YOLO; YOLO('yolo11x.pt')"
```

### 3. Install Redis

```bash
# Option A: Via Docker (recommended)
docker run -d -p 6379:6379 redis:latest

# Option B: Via package manager
bash install_redis.sh
```

---

## Backend Setup

### Start All Services

```bash
cd Heaven
docker-compose up -d
```

**Services Started:**
- FastAPI (port 8000) - REST API
- Redis (port 6379) - Real-time data
- PostgreSQL (port 5432) - Persistent storage
- GraphHopper (port 8989) - Routing engine
- OSRM (port 5000) - Routing engine

### Verify Backend

```bash
# Check health
curl http://localhost:8000/health

# Check API docs
open http://localhost:8000/docs

# Check services
docker-compose ps
```

### Seed Database (First Time Only)

```bash
# Run seed script
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow < seed_data.sql
```

---

## Vision Engine Setup

### 1. Configure Video Source

Edit `VisionEngine/config/config.yaml`:

```yaml
video:
  source: your_video.mp4  # Path to traffic video
  display_preview: true
  target_fps: 15
```

### 2. Define ROIs (Regions of Interest)

```bash
cd VisionEngine
python scripts/roi_editor.py --config config/config.yaml
```

**Instructions:**
- Click to add points
- Right-click to close polygon
- Press 'R' for rectangle mode
- Press 'G' for grid generation
- Press 'S' to save
- Press 'Q' to quit

### 3. Calibrate Speed Detection (Optional)

```bash
python scripts/calibrate_speed.py --config config/config.yaml
```

Click start and end of a known distance, enter real-world meters.

### 4. Run Detection

```bash
# Traffic monitoring
python scripts/detector.py --config config/config.yaml

# Parking monitoring  
python scripts/parking_detector.py --config config/config_parking.yaml
```

---

## Integration

### Data Flow

```
📹 Vision Engine (Python)
    ↓ (publishes to Redis)
🔴 Redis (key-value store)
    ↓ (reads from Redis)
🧠 Backend API (FastAPI)
    ↓ (exposes JSON)
🌐 REST API
    ↓ (consumes API)
💻 Frontend (to be built)
```

### Redis Keys

**Traffic:**
```
urbanflow:traffic:street_1  → "0.21" (congestion score)
urbanflow:traffic:street_2  → "0.55"
urbanflow:traffic:street_3  → "0.80"
urbanflow:traffic:street_4  → "0.30"
```

**Parking:**
```
urbanflow:parking:total_spots     → "18"
urbanflow:parking:occupied_spots  → "11"
urbanflow:parking:available_spots → "7"
urbanflow:parking:occupancy_rate  → "61.1"
urbanflow:parking:spot_SPOT_A1    → "occupied" or "free"
```

### API Endpoints

**Get Live Status:**
```bash
GET http://localhost:8000/api/v1/status/live
```

Response includes:
- `streets[]` - Traffic congestion per street
- `parking_zones[]` - Parking occupancy
- `emergency_vehicles[]` - Active emergencies

**Calculate Route:**
```bash
POST http://localhost:8000/api/v1/route/calculate
Content-Type: application/json

{
  "origin": {"lat": 40.7589, "lon": -73.9762},
  "destination": {"lat": 40.7609, "lon": -73.9762},
  "mode": "citizen"  // or "emergency"
}
```

---

## Troubleshooting

### Backend not responding

```bash
# Check if services are running
docker-compose ps

# Restart services
docker-compose restart

# View logs
docker-compose logs -f api
```

### Vision Engine not detecting

```bash
# Lower confidence threshold in config.yaml
model:
  confidence: 0.1  # Try lower values

# Check video file
ls -lh your_video.mp4

# Test YOLO installation
python -c "from ultralytics import YOLO; print(YOLO('yolo11x.pt'))"
```

### Redis connection refused

```bash
# Check if Redis is running
docker ps | grep redis

# Start Redis if not running
docker-compose up -d redis

# Test connection
python -c "import redis; r=redis.Redis(); print(r.ping())"
```

### Port conflicts

```bash
# Check what's using ports
sudo lsof -i :8000  # FastAPI
sudo lsof -i :6379  # Redis
sudo lsof -i :5432  # PostgreSQL

# Stop conflicting services
sudo systemctl stop postgresql
sudo systemctl stop redis-server
```

### Database is empty

```bash
# Seed the database
cd Heaven
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow < seed_data.sql

# Verify data
docker exec -it urbanflow-postgres psql -U postgres -d urbanflow
SELECT * FROM urbanflow.street_segments;
```

---

## Performance Tuning

### For Higher FPS

```yaml
video:
  target_fps: 30  # Increase from 15

model:
  device: cuda  # Use GPU
```

### For Better Accuracy

```yaml
model:
  weights: yolo11x.pt  # Largest model (slowest)
  confidence: 0.05     # Lower threshold
```

### For Lower CPU Usage

```yaml
video:
  target_fps: 5  # Process fewer frames

model:
  weights: yolo11n.pt  # Smallest model (fastest)
```

---

## Next Steps

1. ✅ Backend running
2. ✅ Vision Engine configured
3. ✅ Data flowing through Redis
4. ✅ API responding
5. ⏳ **Build Frontend UI** (see FOR_DEVELOPERS.md)

---

**For frontend development, see:** `FOR_DEVELOPERS.md`  
**For detailed features, see:** `USER_GUIDE.md`

