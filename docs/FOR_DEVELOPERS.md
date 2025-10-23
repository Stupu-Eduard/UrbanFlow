# 👨‍💻 UrbanFlowAI - Developer Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [API Documentation](#api-documentation)
4. [Frontend Development](#frontend-development)
5. [Contributing](#contributing)

---

## Project Overview

###What's Built

UrbanFlowAI is an AI-powered traffic and parking management system with:

✅ **Vision Engine** - Real-time vehicle detection (YOLO11x)  
✅ **Traffic Monitoring** - Congestion scoring for 4 streets  
✅ **Parking Detection** - Occupancy tracking for 18 spots  
✅ **Speed Tracking** - Vehicle speed measurement  
✅ **Backend API** - FastAPI + Redis + PostgreSQL  
✅ **Routing Services** - OSRM + GraphHopper  
✅ **Real-time Data** - Sub-second latency pipeline  

⏳ **Frontend UI** - Awaiting development (your job!)

### Tech Stack

**Vision Engine:**
- Python 3.13
- YOLOv11 (Ultralytics)
- OpenCV
- Redis client

**Backend:**
- FastAPI (Python)
- Redis (real-time cache)
- PostgreSQL + PostGIS (persistent storage)
- Docker (containerization)
- OSRM & GraphHopper (routing)

**Frontend (to build):**
- Your choice: React, Vue, or vanilla JS
- Leaflet/Mapbox for maps
- WebSocket or polling for real-time updates

---

## System Architecture

### Data Flow

```
┌─────────────────────────────────────────────┐
│          URBANFLOWAI ARCHITECTURE           │
└─────────────────────────────────────────────┘

📹 Vision Engine (Python)
   ├─ detector.py          → Processes traffic video
   ├─ parking_detector.py  → Processes parking video
   └─ metrics_logger.py    → Collects analytics
          ↓ (publishes to Redis)
          
🔴 Redis (In-Memory Cache)
   ├─ urbanflow:traffic:*   → Traffic data
   ├─ urbanflow:parking:*   → Parking data
   └─ urbanflow:emergency:* → Emergency vehicles
          ↓ (reads from Redis)
          
🧠 Backend API (FastAPI)
   ├─ /api/v1/status/live   → Combines Redis + DB
   ├─ /api/v1/route/*       → Routing endpoints
   └─ /health               → System health
          ↓ (exposes REST API)
          
🌐 REST API (JSON over HTTP)
   ├─ GET /api/v1/status/live
   ├─ POST /api/v1/route/calculate
   └─ WebSocket /ws/live (future)
          ↓ (consumed by)
          
💻 Frontend (TO BUILD)
   ├─ Live traffic map
   ├─ Parking dashboard
   └─ Statistics panels
```

### Component Responsibilities

| Component | Responsibility | Language | Port |
|-----------|---------------|----------|------|
| Vision Engine | Detect vehicles, calculate metrics | Python | - |
| Redis | Store real-time data | - | 6379 |
| PostgreSQL | Store city map, persistent data | SQL | 5432 |
| FastAPI | Expose REST API | Python | 8000 |
| OSRM | Route calculation (citizen mode) | C++ | 5000 |
| GraphHopper | Route calculation (emergency) | Java | 8989 |
| Frontend | User interface | JS/TS | 3000 |

---

## API Documentation

### Base URL

```
http://localhost:8000
```

### Interactive Docs

```
http://localhost:8000/docs  (Swagger UI)
http://localhost:8000/redoc (ReDoc)
```

### Main Endpoints

#### 1. Get Live City Status

```http
GET /api/v1/status/live
```

**Response:**
```json
{
  "timestamp": "2025-10-23T15:30:00.000Z",
  "streets": [
    {
      "street_id": "street_1",
      "street_name": "Main Intersection - North",
      "congestion_score": 0.21,
      "congestion_level": "low",
      "coordinates": [[-73.98, 40.75], [-73.97, 40.76]],
      "max_speed": 50
    },
    {
      "street_id": "street_2",
      "street_name": "Main Intersection - South",
      "congestion_score": 0.55,
      "congestion_level": "medium",
      "coordinates": [[-147.96, 40.75], [-147.94, 40.76]],
      "max_speed": 50
    }
  ],
  "average_congestion": 0.44,
  "parking_zones": [
    {
      "zone_id": "zone_A",
      "zone_name": "Central Parking Lot",
      "total_spots": 10,
      "free_spots": 4,
      "occupancy_rate": 0.6,
      "latitude": 40.7589,
      "longitude": -73.9762,
      "spots": [
        {
          "spot_id": "SPOT_A1",
          "status": "occupied"
        },
        {
          "spot_id": "SPOT_A2",
          "status": "free"
        }
      ]
    }
  ],
  "total_parking_spots": 18,
  "total_free_spots": 7,
  "emergency_vehicles": [],
  "active_emergencies": 0
}
```

**Congestion Levels:**
- `low`: 0-40% (green)
- `medium`: 40-60% (yellow)
- `high`: 60-80% (orange)
- `critical`: 80-100% (red)

#### 2. Calculate Route

```http
POST /api/v1/route/calculate
Content-Type: application/json

{
  "origin": {
    "lat": 40.7589,
    "lon": -73.9762
  },
  "destination": {
    "lat": 40.7609,
    "lon": -73.9762
  },
  "mode": "citizen"  // or "emergency"
}
```

**Response:**
```json
{
  "route": {
    "distance": 2.3,  // km
    "duration": 420,  // seconds
    "coordinates": [[...], [...]]
  },
  "engine": "osrm"  // or "graphhopper" for emergency
}
```

#### 3. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-23T15:30:00.000Z",
  "services": {
    "redis": "connected",
    "database": "connected",
    "osrm": "available",
    "graphhopper": "available"
  }
}
```

### Data Models

#### Street Object

```typescript
interface Street {
  street_id: string;          // "street_1", "street_2", etc.
  street_name: string;         // "Main Intersection - North"
  congestion_score: number;    // 0.0 to 1.0
  congestion_level: string;    // "low", "medium", "high", "critical"
  coordinates: number[][];     // [[lng, lat], [lng, lat]]
  max_speed: number;           // Speed limit in km/h
}
```

#### Parking Zone Object

```typescript
interface ParkingZone {
  zone_id: string;         // "zone_A", "zone_B"
  zone_name: string;       // "Central Parking Lot"
  total_spots: number;     // 10
  free_spots: number;      // 4
  occupancy_rate: number;  // 0.6 (60%)
  latitude: number;
  longitude: number;
  spots: ParkingSpot[];
}

interface ParkingSpot {
  spot_id: string;   // "SPOT_A1"
  status: string;    // "occupied" or "free"
}
```

### Real-Time Updates

The API data updates automatically as the Vision Engine processes frames.

**Recommended Update Strategy:**

```javascript
// Fetch every 2 seconds
setInterval(async () => {
  const response = await fetch('http://localhost:8000/api/v1/status/live');
  const data = await response.json();
  updateDashboard(data);
}, 2000);
```

**Alternative: WebSocket (future enhancement)**

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/live');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateDashboard(data);
};
```

---

## Frontend Development

### Requirements

**Must Have (MVP):**

1. **Live Traffic Map**
   - Display 4 streets with color-coded congestion
   - Update every 2 seconds
   - Show congestion percentage per street
   - Color scheme: 🟢 Green (0-40%), 🟡 Yellow (40-60%), 🟠 Orange (60-80%), 🔴 Red (80-100%)

2. **Parking Dashboard**
   - Show 2 parking zones (Central & North)
   - Display total/occupied/free spots
   - Show occupancy percentage
   - List individual spot statuses

3. **Statistics Panel**
   - Average city congestion
   - Total vehicles detected
   - Parking availability summary

**Nice to Have (Post-MVP):**
- Emergency vehicle alerts
- Historical data charts
- Speed violation notifications
- Route calculator interface
- Admin controls

### Technology Recommendations

#### Option 1: React + Leaflet (Recommended)

**Why:** Industry standard, great ecosystem, excellent for real-time.

```bash
npx create-react-app urbanflow-dashboard
cd urbanflow-dashboard
npm install axios leaflet react-leaflet chart.js
```

**Sample Code:**

```jsx
import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polyline } from 'react-leaflet';
import axios from 'axios';

function TrafficMap() {
  const [streets, setStreets] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const { data } = await axios.get('http://localhost:8000/api/v1/status/live');
      setStreets(data.streets);
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const getColor = (score) => {
    if (score < 0.4) return '#00FF00'; // green
    if (score < 0.6) return '#FFFF00'; // yellow
    if (score < 0.8) return '#FFA500'; // orange
    return '#FF0000'; // red
  };

  return (
    <MapContainer center={[40.7589, -73.9762]} zoom={13}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {streets.map(street => (
        <Polyline
          key={street.street_id}
          positions={street.coordinates.map(([lng, lat]) => [lat, lng])}
          color={getColor(street.congestion_score)}
          weight={5}
        />
      ))}
    </MapContainer>
  );
}
```

#### Option 2: Vue.js + OpenLayers

**Why:** Simpler learning curve, good performance.

```bash
npm create vue@latest urbanflow-dashboard
cd urbanflow-dashboard
npm install axios ol
```

#### Option 3: Vanilla HTML + JavaScript

**Why:** Fastest MVP, no build tools.

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>
  <div id="map" style="height: 600px;"></div>
  <script>
    const map = L.map('map').setView([40.7589, -73.9762], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    async function updateMap() {
      const response = await fetch('http://localhost:8000/api/v1/status/live');
      const data = await response.json();
      
      // Draw streets
      data.streets.forEach(street => {
        const color = street.congestion_score < 0.4 ? '#00FF00' : '#FF0000';
        L.polyline(street.coordinates.map(([lng, lat]) => [lat, lng]), { color }).addTo(map);
      });
    }

    updateMap();
    setInterval(updateMap, 2000);
  </script>
</body>
</html>
```

### UI Mockup

```
┌─────────────────────────────────────────────────────────┐
│  UrbanFlowAI - Live Dashboard                      [⚙️] │
├────────────────────────┬────────────────────────────────┤
│                        │  📊 STATISTICS                 │
│   🗺️  TRAFFIC MAP      │  ┌──────────────────────────┐ │
│  ┌──────────────────┐  │  │ Avg Congestion: 44.3%   │ │
│  │                  │  │  │ Total Vehicles: 53      │ │
│  │  [Interactive    │  │  │ Active Emergencies: 0   │ │
│  │   Map Here]      │  │  └──────────────────────────┘ │
│  │                  │  │                                │
│  │  Streets:        │  │  🅿️  PARKING ZONES            │
│  │  ■ Street 1: 21% │  │  ┌──────────────────────────┐ │
│  │  ■ Street 2: 55% │  │  │ Zone A: [■■■■■■□□□□]   │ │
│  │  ■ Street 3: 80% │  │  │ 60% Full (6/10 spots)   │ │
│  │  ■ Street 4: 30% │  │  │                          │ │
│  └──────────────────┘  │  │ Zone B: [■■■■■■■■□□]   │ │
│                        │  │ 80% Full (8/10 spots)   │ │
│  🔄 Last: 2s ago       │  └──────────────────────────┘ │
└────────────────────────┴────────────────────────────────┘
```

### CORS Configuration

The backend already allows CORS from `localhost`.

If you need to add other origins, edit `Heaven/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Testing the API

```bash
# Get live status
curl http://localhost:8000/api/v1/status/live | jq

# Calculate route
curl -X POST http://localhost:8000/api/v1/route/calculate \
  -H "Content-Type: application/json" \
  -d '{"origin":{"lat":40.7589,"lon":-73.9762},"destination":{"lat":40.7609,"lon":-73.9762},"mode":"citizen"}'
```

---

## Contributing

### Project Structure

```
UrbanFlow/
├── Heaven/                    # Backend (FastAPI)
│   ├── api/                   # API endpoints
│   ├── docker-compose.yml     # Infrastructure
│   └── init-db/               # Database setup
├── VisionEngine/              # Vision processing
│   ├── scripts/               # Python scripts
│   │   ├── detector.py        # Main traffic detector
│   │   ├── parking_detector.py # Parking detector
│   │   ├── roi_editor.py      # ROI configuration tool
│   │   └── calibrate_speed.py # Speed calibration
│   ├── config/                # Configuration files
│   │   ├── config.yaml        # Traffic config
│   │   └── config_parking.yaml # Parking config
│   ├── metrics/               # Output directory
│   └── requirements.txt       # Python dependencies
└── docs/                      # Documentation
    ├── SETUP_GUIDE.md         # Installation & setup
    ├── USER_GUIDE.md          # User manual
    └── FOR_DEVELOPERS.md      # This file
```

### Development Workflow

**1. Backend Development:**

```bash
# Make changes to Heaven/api/*
cd Heaven
docker-compose restart api
docker-compose logs -f api
```

**2. Vision Engine Development:**

```bash
# Make changes to VisionEngine/scripts/*
cd VisionEngine
python scripts/detector.py
```

**3. Frontend Development:**

```bash
# Create your frontend app
npx create-react-app frontend
cd frontend
npm start
```

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Keep functions < 50 lines

**JavaScript/TypeScript:**
- Use ES6+ syntax
- Prefer async/await over callbacks
- Use functional components (React)
- Add JSDoc comments

### Testing

**Backend:**
```bash
# Run tests
cd Heaven
pytest

# API testing
curl http://localhost:8000/health
```

**Vision Engine:**
```bash
# Test on sample video
python scripts/detector.py --config config/config.yaml
```

**Integration:**
```bash
# Full system test
./test_integration.sh
```

### Pull Request Guidelines

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add my feature"`
4. Push to branch: `git push origin feature/my-feature`
5. Open Pull Request

**PR Requirements:**
- Clear description of changes
- Tests pass
- Documentation updated
- Code follows style guide

---

## Performance Considerations

### API Response Time

**Target:** < 100ms for `/api/v1/status/live`

**Actual:** ~50ms (Redis read + JSON serialization)

### Update Frequency

**Vision Engine:** 15 FPS (every 66ms)  
**Redis:** Updated every frame  
**Frontend polling:** Recommended 2 seconds  
**API processing:** < 1ms

### Scaling

**Horizontal:**
- Add more Vision Engine instances (different videos)
- Load balance FastAPI with Nginx
- Redis Cluster for high availability

**Vertical:**
- Use GPU for Vision Engine (CUDA)
- Increase target_fps
- Use larger YOLO model

---

## Deployment

### Production Considerations

**Security:**
- Add API authentication (JWT)
- Enable HTTPS (SSL certificates)
- Secure Redis with password
- Use environment variables for secrets

**Monitoring:**
- Prometheus + Grafana
- Log aggregation (ELK stack)
- Uptime monitoring

**Infrastructure:**
- Cloud deployment (AWS/Azure/GCP)
- Kubernetes for orchestration
- CI/CD pipeline (GitHub Actions)

### Environment Variables

```bash
# Backend
REDIS_HOST=localhost
REDIS_PORT=6379
DATABASE_URL=postgresql://user:pass@localhost:5432/urbanflow

# Vision Engine
VIDEO_SOURCE=/path/to/video.mp4
MODEL_WEIGHTS=yolo11x.pt
CONFIDENCE_THRESHOLD=0.1
```

---

## Support

**Documentation:**
- `SETUP_GUIDE.md` - Installation instructions
- `USER_GUIDE.md` - Feature documentation
- `FOR_DEVELOPERS.md` - This file

**API Docs:**
- http://localhost:8000/docs

**Issues:**
- GitHub Issues: Report bugs or request features

---

**Ready to build the frontend? Start with `/api/v1/status/live` and display streets on a map!** 🚀

