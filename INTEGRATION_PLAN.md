# 🔗 UrbanFlowAI - Complete Integration Plan

**Connecting Vision Engine → Backend → Database**

**Date:** October 23, 2025  
**Status:** Ready to Integrate ✅

---

## 📊 System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     UrbanFlowAI System                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📹 Vision Engine (Role 1 - COMPLETED)                          │
│  /home/teodor/UrbanFlow/                                         │
│     ├─ detector.py           (Traffic monitoring)                │
│     ├─ parking_detector.py   (Parking monitoring)                │
│     └─ metrics_logger.py     (Metrics collection)                │
│                     │                                             │
│                     ▼                                             │
│  🔴 Redis (localhost:6379)                                       │
│     ├─ urbanflow:traffic:street_1 = "0.75"                      │
│     ├─ urbanflow:parking:SPOT_A1 = "free"                       │
│     └─ urbanflow:emergency:truck_01 = {...}                     │
│                     │                                             │
│                     ▼                                             │
│  🧠 Backend (Role 2 - TO BE STARTED)                            │
│  /home/teodor/UrbanFlow_Backend/Heaven/                          │
│     ├─ FastAPI (port 8000)                                       │
│     ├─ PostgreSQL + PostGIS                                      │
│     ├─ OSRM (routing)                                            │
│     └─ GraphHopper (emergency routing)                           │
│                     │                                             │
│                     ▼                                             │
│  🌐 REST API                                                     │
│     ├─ GET /api/v1/status/live                                   │
│     ├─ POST /api/v1/route/calculate                              │
│     └─ GET /health                                               │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## ✅ Data Format Compatibility

| Data Type | Vision Engine Output | Backend Expects | Status |
|-----------|---------------------|-----------------|--------|
| **Traffic** | `urbanflow:traffic:street_1` = `"0.75"` | `urbanflow:traffic:street_1` | ✅ PERFECT MATCH |
| **Parking** | `urbanflow:parking:SPOT_A1` = `"free"` | `urbanflow:parking:SPOT_A1` | ✅ PERFECT MATCH |
| **Emergency** | `urbanflow:emergency:truck_01` = JSON | `urbanflow:emergency:truck_01` | ✅ PERFECT MATCH |
| **Metrics** | `metrics/*.json`, `metrics/*.csv` | Not used by backend | ✅ Independent |

**Result:** **NO CODE CHANGES NEEDED!** The formats already align! 🎉

---

## 📋 Integration Steps

### Phase 1: Backend Setup (15 minutes)

**Step 1.1: Install Docker (if not already)**
```bash
# Check if Docker is installed
docker --version
docker-compose --version

# If not installed:
# sudo apt install docker.io docker-compose
# sudo systemctl start docker
# sudo systemctl enable docker
```

**Step 1.2: Start Backend Services**
```bash
cd /home/teodor/UrbanFlow_Backend/Heaven

# Start all services (Redis, PostgreSQL, API, OSRM, GraphHopper)
docker-compose up -d

# Wait for services to start (2-3 minutes)
docker-compose logs -f
```

**Step 1.3: Verify Backend Health**
```bash
# Check all services are running
docker-compose ps

# Test API health
curl http://localhost:8000/health

# Test interactive docs
# Open in browser: http://localhost:8000/docs
```

---

### Phase 2: Redis Connection (5 minutes)

**Step 2.1: Verify Redis is Running**
```bash
# Redis should be running in Docker
docker-compose ps redis

# Test connection
redis-cli -h localhost -p 6379 ping
# Should return: PONG
```

**Step 2.2: Configure Vision Engine**

Our Vision Engine already connects to `localhost:6379` - no changes needed!

```yaml
# config.yaml (already correct)
redis:
  host: localhost
  port: 6379
  db: 0
```

---

### Phase 3: End-to-End Testing (10 minutes)

**Step 3.1: Start Vision Engine**
```bash
cd /home/teodor/UrbanFlow
python detector.py
```

**Expected output:**
```
✓ Connected to Redis at localhost:6379
```

**Step 3.2: Verify Data Flow**

Open 3 terminals:

**Terminal 1: Vision Engine**
```bash
cd /home/teodor/UrbanFlow
python detector.py
# Should show detections and publish to Redis
```

**Terminal 2: Monitor Redis**
```bash
# Watch data being written
redis-cli
> KEYS urbanflow:*
> GET urbanflow:traffic:street_1
> GET urbanflow:parking:SPOT_A1
> MONITOR  # Shows all Redis commands in real-time
```

**Terminal 3: Check Backend API**
```bash
# Backend should read from Redis and expose via API
curl http://localhost:8000/api/v1/status/live | jq

# Should return JSON with:
# - streets: [...]
# - parking_zones: [...]
# - emergency_vehicles: [...]
```

**Step 3.3: Verify Database**
```bash
# Check PostgreSQL is storing data
docker exec -it urbanflow-postgres psql -U urbanflow -d urbanflow

# Run queries:
SELECT * FROM street_segments;
SELECT * FROM parking_zones;
SELECT * FROM parking_spots;
```

---

### Phase 4: Production Configuration (Optional)

**Update Backend Environment Variables**

Edit `/home/teodor/UrbanFlow_Backend/Heaven/docker-compose.yml`:

```yaml
api:
  environment:
    - LOG_LEVEL=INFO  # Change to DEBUG for troubleshooting
    - REDIS_HOST=redis
    - POSTGRES_DB=urbanflow
    # Add more as needed
```

---

## 🔧 Integration Commands

### Quick Start (All-in-One)

Create `/home/teodor/start_urbanflow.sh`:

```bash
#!/bin/bash
echo "🚀 Starting UrbanFlowAI Complete System"
echo "========================================"

# Start Backend (Redis, PostgreSQL, API)
echo "📦 Starting Backend..."
cd /home/teodor/UrbanFlow_Backend/Heaven
docker-compose up -d

# Wait for services
echo "⏳ Waiting for backend to be ready..."
sleep 10

# Check health
echo "🏥 Checking backend health..."
curl -s http://localhost:8000/health | jq

# Start Vision Engine
echo "👁️  Starting Vision Engine..."
cd /home/teodor/UrbanFlow
python detector.py
```

Make it executable:
```bash
chmod +x /home/teodor/start_urbanflow.sh
```

Run it:
```bash
/home/teodor/start_urbanflow.sh
```

---

## 📊 Data Flow Verification

### Test 1: Traffic Data

```bash
# 1. Vision Engine publishes traffic
# (detector.py automatically does this)

# 2. Check Redis
redis-cli GET "urbanflow:traffic:street_1"
# Expected: "0.75" (or similar density value)

# 3. Check Backend API
curl http://localhost:8000/api/v1/status/live | jq '.streets'
# Expected: [{"street_id": "street_1", "congestion": 0.75, ...}]
```

### Test 2: Parking Data

```bash
# 1. Vision Engine publishes parking
# (parking_detector.py automatically does this)

# 2. Check Redis
redis-cli GET "urbanflow:parking:SPOT_A1"
# Expected: "free" or "occupied"

# 3. Check Backend API
curl http://localhost:8000/api/v1/status/live | jq '.parking_zones'
# Expected: [{"zone_id": "zone_A", "free_spots": 12, ...}]
```

### Test 3: Emergency Vehicles

```bash
# 1. Check Redis (5s TTL)
redis-cli KEYS "urbanflow:emergency:truck_*"
redis-cli GET "urbanflow:emergency:truck_01"
# Expected: JSON with location data

# 2. Check Backend API
curl http://localhost:8000/api/v1/status/live | jq '.emergency_vehicles'
# Expected: [{"id": "truck_01", "location": {...}, ...}]
```

---

## 🐛 Troubleshooting

### Problem: Backend can't connect to Redis

**Symptoms:**
```bash
curl http://localhost:8000/health
# Returns error or "unhealthy"
```

**Solution:**
```bash
# Check Redis is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Restart Redis
docker-compose restart redis
```

---

### Problem: Vision Engine can't connect to Redis

**Symptoms:**
```
⚠ Warning: Could not connect to Redis: Connection refused
```

**Solution:**
```bash
# Check if Redis is running
docker-compose ps redis

# If not running, start it
cd /home/teodor/UrbanFlow_Backend/Heaven
docker-compose up -d redis

# Test connection
redis-cli -h localhost -p 6379 ping
```

---

### Problem: Data not flowing to backend

**Symptoms:**
```bash
curl http://localhost:8000/api/v1/status/live
# Returns empty data
```

**Solution:**
```bash
# 1. Check Vision Engine is running
ps aux | grep detector.py

# 2. Check Redis has data
redis-cli KEYS "urbanflow:*"

# 3. Check backend logs
docker-compose logs api

# 4. Restart API
docker-compose restart api
```

---

## 📁 Directory Structure After Integration

```
/home/teodor/
├── UrbanFlow/                     # Vision Engine (Role 1)
│   ├── detector.py
│   ├── parking_detector.py
│   ├── metrics_logger.py
│   ├── config.yaml
│   ├── config_parking.yaml
│   └── metrics/
│       ├── current_metrics.json
│       └── metrics_history.csv
│
└── UrbanFlow_Backend/             # Backend (Role 2)
    └── Heaven/
        ├── docker-compose.yml
        ├── api/
        ├── init-db/
        └── docs/ (*.md files)
```

---

## ✅ Integration Checklist

### Backend Setup
- [ ] Docker installed
- [ ] Backend repository cloned (`/home/teodor/UrbanFlow_Backend/`)
- [ ] Docker Compose services started (`docker-compose up -d`)
- [ ] Backend health check passing (`curl http://localhost:8000/health`)
- [ ] Redis running and accessible (`redis-cli ping`)
- [ ] PostgreSQL running (`docker-compose ps postgres`)

### Vision Engine Configuration
- [x] Redis connection configured (localhost:6379) ✅
- [x] Redis keys use correct format (`urbanflow:*`) ✅
- [x] Traffic monitoring working ✅
- [x] Parking monitoring working ✅
- [x] Metrics logging enabled ✅

### Data Flow Verification
- [ ] Vision Engine connects to Redis (no warnings)
- [ ] Redis contains `urbanflow:*` keys
- [ ] Backend API returns live data (`/api/v1/status/live`)
- [ ] Traffic data appears in API response
- [ ] Parking data appears in API response
- [ ] Emergency vehicles appear when detected

### End-to-End Testing
- [ ] Run `detector.py` → Check API shows traffic data
- [ ] Run `parking_detector.py` → Check API shows parking data
- [ ] Monitor Redis (`MONITOR` command) shows data flow
- [ ] Check metrics files are being generated
- [ ] Verify database contains city map data

---

## 🚀 Production Deployment Considerations

### Security
- [ ] Change default PostgreSQL password
- [ ] Add API authentication (JWT)
- [ ] Enable HTTPS (nginx + Let's Encrypt)
- [ ] Restrict Redis access (requirepass)
- [ ] Add rate limiting to API

### Performance
- [ ] Optimize YOLO model size (use yolo11n for speed)
- [ ] Add Redis connection pooling
- [ ] Enable PostgreSQL query caching
- [ ] Add CDN for API responses
- [ ] Monitor resource usage (CPU, RAM, GPU)

### Monitoring
- [ ] Add Prometheus metrics
- [ ] Set up Grafana dashboards
- [ ] Configure log aggregation (ELK stack)
- [ ] Add uptime monitoring
- [ ] Set up alerting (PagerDuty, etc.)

### Scalability
- [ ] Add Redis cluster for high availability
- [ ] PostgreSQL replication
- [ ] Load balancer for API
- [ ] Multiple Vision Engine instances
- [ ] Kubernetes deployment (optional)

---

## 📞 Support & Documentation

### Vision Engine Docs
- `/home/teodor/UrbanFlow/README.md`
- `/home/teodor/UrbanFlow/BACKEND_INTEGRATION.md`
- `/home/teodor/UrbanFlow/METRICS_GUIDE.md`

### Backend Docs
- `/home/teodor/UrbanFlow_Backend/Heaven/START_HERE.md`
- `/home/teodor/UrbanFlow_Backend/Heaven/API_DOCUMENTATION.md`
- `/home/teodor/UrbanFlow_Backend/Heaven/DATA_CONTRACTS.md`
- `/home/teodor/UrbanFlow_Backend/Heaven/ARCHITECTURE.md`

### Quick Commands
```bash
# Start everything
cd /home/teodor/UrbanFlow_Backend/Heaven && docker-compose up -d
cd /home/teodor/UrbanFlow && python detector.py

# Stop everything
pkill -f detector.py
cd /home/teodor/UrbanFlow_Backend/Heaven && docker-compose down

# Check logs
docker-compose logs -f api
docker-compose logs -f redis

# Monitor Redis
redis-cli MONITOR

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/status/live | jq
```

---

## 🎯 Success Criteria

Integration is successful when:

✅ Vision Engine runs without Redis connection errors  
✅ Backend API returns live traffic data  
✅ Backend API returns live parking data  
✅ Emergency vehicles appear in API when detected  
✅ Data updates in real-time (< 1 second latency)  
✅ PostgreSQL database is populated  
✅ All Docker containers are healthy  
✅ API documentation is accessible (http://localhost:8000/docs)  

---

## 🎉 Next Steps After Integration

1. **Frontend Integration** (Role 3)
   - Build dashboard to consume API
   - Display live traffic map
   - Show parking availability
   - Track emergency vehicles

2. **Map Data Setup**
   - Load real city map into PostgreSQL
   - Configure OSRM with city streets
   - Configure GraphHopper with emergency routes

3. **Production Deployment**
   - Set up cloud infrastructure
   - Configure CI/CD pipeline
   - Add monitoring and alerting
   - Security hardening

4. **Testing & Optimization**
   - Load testing
   - Performance optimization
   - Bug fixes and improvements

---

**Integration should take approximately 30 minutes total!** 🚀

---

*UrbanFlowAI - Making Cities Smarter* 🧠✨

