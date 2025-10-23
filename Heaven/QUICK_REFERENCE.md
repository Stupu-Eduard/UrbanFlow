# UrbanFlowAI Quick Reference Card

## 🚀 One-Command Start

**Windows:**
```cmd
quickstart.bat
```

**Linux/Mac:**
```bash
./quickstart.sh
```

## 📍 Important URLs

| Service | URL |
|---------|-----|
| API Documentation | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |
| Live Status | http://localhost:8000/api/v1/status/live |

## 🔧 Common Commands

### Docker Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f api

# Restart a service
docker-compose restart api

# Check service status
docker-compose ps
```

### Database Management
```bash
# Seed with sample data
curl -X POST http://localhost:8000/api/v1/admin/seed-data

# Seed Redis
curl -X POST http://localhost:8000/api/v1/admin/seed-redis

# Check Redis status
curl http://localhost:8000/api/v1/admin/redis-status
```

### Testing Endpoints
```bash
# Get live city status
curl http://localhost:8000/api/v1/status/live | jq

# Calculate citizen route
curl -X POST http://localhost:8000/api/v1/route/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"latitude": 40.7489, "longitude": -73.9852},
    "end": {"latitude": 40.7599, "longitude": -73.9762},
    "mode": "citizen"
  }' | jq

# Calculate emergency route
curl -X POST http://localhost:8000/api/v1/route/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"latitude": 40.7489, "longitude": -73.9852},
    "end": {"latitude": 40.7599, "longitude": -73.9762},
    "mode": "emergency",
    "vehicle_id": "truck_01"
  }' | jq
```

## 📊 Redis Data Formats (for Role 1)

### Traffic
```python
r.set('urbanflow:traffic:street_1', '0.75')
```

### Parking
```python
r.set('urbanflow:parking:SPOT_A1', 'free')
```

### Emergency Vehicles
```python
import json, time
data = {
    "id": "truck_01",
    "location": [640, 320],
    "bbox": [600, 280, 680, 360],
    "timestamp": time.time(),
    "status": "responding"
}
r.setex('urbanflow:emergency:truck_01', 5, json.dumps(data))
```

## 🐛 Quick Troubleshooting

| Problem | Quick Fix |
|---------|-----------|
| Docker not running | Start Docker Desktop |
| Redis connection failed | `docker-compose restart redis` |
| DB connection failed | `docker-compose restart postgres` |
| Empty API response | Run seed commands |
| Port already in use | Change port in docker-compose.yml |

## 📈 Service Ports

| Service | Port |
|---------|------|
| API | 8000 |
| Redis | 6379 |
| PostgreSQL | 5432 |
| OSRM | 5000 |
| GraphHopper | 8989 |

## ✅ Pre-Flight Checklist

- [ ] Docker is running
- [ ] Run `docker-compose up -d`
- [ ] Wait 60-90 seconds for services
- [ ] Seed database: `curl -X POST http://localhost:8000/api/v1/admin/seed-data`
- [ ] Seed Redis: `curl -X POST http://localhost:8000/api/v1/admin/seed-redis`
- [ ] Test: `curl http://localhost:8000/health`
- [ ] Open: http://localhost:8000/docs

## 🔍 Validation

Run configuration check:
```bash
python validate_setup.py
```

## 📚 Documentation

- **Full Guide:** `README.md`
- **Configuration Report:** `CONFIGURATION_REPORT.md`
- **API Documentation:** `API_DOCUMENTATION.md`
- **Architecture:** `ARCHITECTURE.md`
- **Data Contracts:** `DATA_CONTRACTS.md`

---

**Need Help?** Check `CONFIGURATION_REPORT.md` for detailed troubleshooting.


