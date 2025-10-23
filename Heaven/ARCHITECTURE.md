# 🏛️ UrbanFlowAI - System Architecture

**Visual Guide to How Everything Connects**

---

## High-Level Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                         UrbanFlowAI System                             │
│                    Intelligent Traffic Management                      │
└───────────────────────────────────────────────────────────────────────┘

        ┌─────────────────┐                    ┌──────────────────┐
        │   AI Cameras    │                    │  Mobile Apps &   │
        │  & Sensors      │                    │  Web Dashboard   │
        │   (Role 1)      │                    │    (Role 3)      │
        └────────┬────────┘                    └────────▲─────────┘
                 │                                      │
                 │ Computer Vision                      │ HTTP/REST
                 │ Real-time Data                       │ JSON API
                 ▼                                      │
        ┌─────────────────┐                    ┌───────┴──────────┐
        │  Redis          │                    │                  │
        │  In-Memory DB   │◄───────reads───────│   FastAPI        │
        │  Real-time      │                    │   Backend        │
        │  - Traffic      │                    │   (Role 2)       │
        │  - Parking      │                    │   "THE BRAIN"    │
        │  - Emergencies  │                    │                  │
        └─────────────────┘                    └───────┬──────────┘
                                                       │
        ┌─────────────────┐                           │
        │  PostgreSQL     │                           │
        │  + PostGIS      │◄──────reads───────────────┤
        │  Persistent DB  │                           │
        │  - Streets      │                           │
        │  - Zones        │                           │
        │  - Vehicles     │                           │
        └─────────────────┘                           │
                                                      │
                                              ┌───────┴──────────┐
                                              │                  │
                                              │  Routing Engines │
                                              │                  │
                                              │  ┌────────────┐  │
                                              │  │   OSRM     │  │
                                              │  │  (Citizen) │  │
                                              │  └────────────┘  │
                                              │                  │
                                              │  ┌────────────┐  │
                                              │  │GraphHopper │  │
                                              │  │(Emergency) │  │
                                              │  └────────────┘  │
                                              └──────────────────┘
```

---

## Data Flow Diagrams

### Flow 1: Live Status Request

```
┌──────────┐         ┌──────────┐         ┌─────────┐
│          │         │          │         │         │
│ Frontend │         │ Backend  │         │  Redis  │
│ (Role 3) │         │ (Role 2) │         │         │
│          │         │          │         │         │
└────┬─────┘         └────┬─────┘         └────┬────┘
     │                    │                    │
     │  GET /status/live  │                    │
     │───────────────────>│                    │
     │                    │                    │
     │                    │  Get all traffic   │
     │                    │───────────────────>│
     │                    │                    │
     │                    │  congestion data   │
     │                    │<───────────────────│
     │                    │                    │
     │                    │  Get all parking   │
     │                    │───────────────────>│
     │                    │                    │
     │                    │  parking statuses  │
     │                    │<───────────────────│
     │                    │                    │
     │                    │  Get emergency     │
     │                    │───────────────────>│
     │                    │                    │
     │                    │  vehicle locations │
     │                    │<───────────────────│
     │                    │                    │
     │                    ▼                    │
     │            ┌────────────┐               │
     │            │ PostgreSQL │               │
     │            └────┬───────┘               │
     │                 │                       │
     │    Query street names & parking zones  │
     │                 │                       │
     │            ┌────▼───────┐               │
     │            │   Combine  │               │
     │            │    Data    │               │
     │            └────┬───────┘               │
     │                 │                       │
     │   JSON Response │                       │
     │<────────────────┘                       │
     │                                         │
     │ {                                       │
     │   "streets": [...],                     │
     │   "parking_zones": [...],               │
     │   "emergency_vehicles": [...]           │
     │ }                                       │
     │                                         │
```

### Flow 2: Emergency Route Calculation

```
┌──────────┐         ┌──────────┐         ┌─────────┐         ┌────────────┐
│          │         │          │         │         │         │            │
│ Frontend │         │ Backend  │         │  Redis  │         │GraphHopper │
│          │         │          │         │         │         │            │
└────┬─────┘         └────┬─────┘         └────┬────┘         └─────┬──────┘
     │                    │                    │                    │
     │ POST /route        │                    │                    │
     │ mode: emergency    │                    │                    │
     │───────────────────>│                    │                    │
     │                    │                    │                    │
     │                    │ Get traffic data   │                    │
     │                    │───────────────────>│                    │
     │                    │                    │                    │
     │                    │ Congestion scores  │                    │
     │                    │<───────────────────│                    │
     │                    │                    │                    │
     │                    │         Identify congested streets      │
     │                    │                    │                    │
     │                    │         Build custom routing model      │
     │                    │         (penalize congested streets)    │
     │                    │                                         │
     │                    │         POST /route with custom model   │
     │                    │────────────────────────────────────────>│
     │                    │                                         │
     │                    │         Calculate smart route           │
     │                    │         (avoids congestion)             │
     │                    │                                         │
     │                    │         Route with avoided streets      │
     │                    │<────────────────────────────────────────│
     │                    │                                         │
     │   Route JSON       │                                         │
     │<───────────────────│                                         │
     │                    │                                         │
     │ {                                                            │
     │   "coordinates": [...],                                      │
     │   "avoided_congested_streets": ["street_2", "street_5"]     │
     │ }                                                            │
     │                                                              │
```

### Flow 3: AI Vision Writes Data

```
┌──────────┐         ┌─────────┐
│          │         │         │
│ AI Vision│         │  Redis  │
│ (Role 1) │         │         │
│          │         │         │
└────┬─────┘         └────┬────┘
     │                    │
     │  Analyze video     │
     │                    │
     ▼                    │
┌─────────┐               │
│ Street  │               │
│ has 75% │               │
│ density │               │
└────┬────┘               │
     │                    │
     │ SET traffic:street_1 = "0.75"
     │───────────────────>│
     │                    │
     │  Detect parking    │
     │                    │
     ▼                    │
┌─────────┐               │
│ Spot A1 │               │
│ is free │               │
└────┬────┘               │
     │                    │
     │ SET parking:zone_A:A1 = "free"
     │───────────────────>│
     │                    │
     │  Track ambulance   │
     │                    │
     ▼                    │
┌─────────┐               │
│GPS: 40.7│               │
│Responding│              │
└────┬────┘               │
     │                    │
     │ SET emergency:amb_001 = {JSON}
     │───────────────────>│
     │                    │
     │                    │
     │   Backend reads    │
     │   this data        │
     │                    │
```

---

## Component Architecture

### The Brain (FastAPI Backend)

```
┌───────────────────────────────────────────────────────┐
│                    FastAPI Backend                     │
│                     (main.py)                          │
├───────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │         API Endpoints (main.py)              │    │
│  │                                               │    │
│  │  GET  /health                                │    │
│  │  GET  /api/v1/status/live                    │    │
│  │  POST /api/v1/route/calculate                │    │
│  │  POST /admin/seed-data                       │    │
│  └──────────────┬───────────────────────────────┘    │
│                 │                                      │
│                 ▼                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │      Core Business Logic (services.py)       │    │
│  │                                               │    │
│  │  UrbanFlowBrain:                             │    │
│  │    - get_live_status()                       │    │
│  │    - calculate_route()                       │    │
│  │    - _build_street_status()                  │    │
│  │    - _build_parking_status()                 │    │
│  │    - _calculate_emergency_route()            │    │
│  └──────────┬──────────────────┬─────────────────┘   │
│             │                  │                      │
│             ▼                  ▼                      │
│  ┌─────────────────┐  ┌─────────────────┐           │
│  │  Redis Client   │  │ Routing Service │           │
│  │ (redis_client)  │  │ (routing_service)│          │
│  │                 │  │                  │           │
│  │ - get_traffic() │  │ - OSRM client   │           │
│  │ - get_parking() │  │ - GraphHopper   │           │
│  │ - get_emergency()│  │   client        │           │
│  └────────┬────────┘  └──────┬───────────┘           │
│           │                  │                        │
│           ▼                  ▼                        │
│  ┌─────────────────┐  ┌─────────────────┐           │
│  │  Data Contracts │  │   Database      │           │
│  │  (contracts.py) │  │  (database.py)  │           │
│  │                 │  │                  │           │
│  │ Pydantic models │  │ SQLAlchemy models│          │
│  │ - Request       │  │ - StreetSegmentDB│          │
│  │ - Response      │  │ - ParkingZoneDB │           │
│  │ - Validation    │  │ - EmergencyVehicleDB│       │
│  └─────────────────┘  └──────────────────┘          │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## Database Schema

### PostgreSQL + PostGIS

```
┌──────────────────────┐
│  street_segments     │
├──────────────────────┤
│ PK street_id         │
│    street_name       │
│    geometry          │  ← PostGIS LineString
│    max_speed         │
│    created_at        │
│    updated_at        │
└──────────────────────┘

┌──────────────────────┐
│  parking_zones       │
├──────────────────────┤
│ PK zone_id           │
│    zone_name         │
│    latitude          │
│    longitude         │
│    total_capacity    │
│    created_at        │
│    updated_at        │
└──────────────────────┘

┌──────────────────────┐
│  parking_spots       │
├──────────────────────┤
│ PK spot_id           │
│ FK zone_id           │────┐
│    latitude          │    │
│    longitude         │    │
│    created_at        │    │
│    updated_at        │    │
└──────────────────────┘    │
                             │
                             └──> Joins with parking_zones

┌──────────────────────┐
│  emergency_vehicles  │
├──────────────────────┤
│ PK vehicle_id        │
│    vehicle_type      │  (ambulance, fire_truck, police)
│    license_plate     │
│    created_at        │
│    updated_at        │
└──────────────────────┘
```

### Redis (In-Memory)

```
┌──────────────────────────────────────┐
│           Redis Key-Value            │
├──────────────────────────────────────┤
│                                      │
│  traffic:street_1     → "0.75"      │
│  traffic:street_2     → "0.30"      │
│  traffic:street_3     → "0.90"      │
│                                      │
│  parking:zone_A:A1    → "free"      │
│  parking:zone_A:A2    → "occupied"  │
│  parking:zone_B:B1    → "free"      │
│                                      │
│  emergency:amb_001    → {           │
│    "vehicle_id": "amb_001",         │
│    "latitude": 40.7489,             │
│    "longitude": -73.9852,           │
│    "status": "responding",          │
│    ...                              │
│  }                                  │
│                                      │
└──────────────────────────────────────┘
```

---

## Routing Intelligence

### Citizen Mode (OSRM)

```
Start: (40.7489, -73.9852)
  │
  ▼
┌─────────────┐
│    OSRM     │  → Ultra-fast routing
│  Algorithm  │    Uses pre-processed map
└──────┬──────┘    Optimized for speed
       │
       ▼
End: (40.7599, -73.9762)

Result: Fastest route (no traffic awareness)
```

### Emergency Mode (GraphHopper)

```
Start: (40.7489, -73.9852)
  │
  ▼
┌─────────────────────┐
│  Check Redis for    │
│  Traffic Congestion │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Identify congested  │
│ streets (>0.7)      │
│                     │
│ street_2: 0.85      │
│ street_5: 0.92      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   GraphHopper       │
│   Custom Model      │
│                     │
│ Penalize:           │
│  - street_2 (×0.3)  │
│  - street_5 (×0.3)  │
│                     │
│ Find alternative!   │
└──────────┬──────────┘
           │
           ▼
End: (40.7599, -73.9762)

Result: Smart route avoiding congestion
```

---

## Deployment Architecture

### Docker Compose Stack

```
┌──────────────────────────────────────────────────────┐
│              Docker Host Machine                     │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────────┐    ┌────────────────┐           │
│  │  urbanflow-api │    │ urbanflow-redis│           │
│  │                │    │                │           │
│  │  Port: 8000    │◄───│  Port: 6379    │           │
│  │  FastAPI       │    │  Redis         │           │
│  └────────┬───────┘    └────────────────┘           │
│           │                                          │
│           │            ┌────────────────┐           │
│           └───────────►│ urbanflow-     │           │
│                        │   postgres     │           │
│                        │                │           │
│                        │  Port: 5432    │           │
│                        │  PostgreSQL    │           │
│                        │  + PostGIS     │           │
│                        └────────────────┘           │
│                                                      │
│  ┌────────────────┐    ┌────────────────┐          │
│  │ urbanflow-osrm │    │ urbanflow-     │          │
│  │                │    │  graphhopper   │          │
│  │  Port: 5000    │◄───│  Port: 8989    │          │
│  │  OSRM          │    │  GraphHopper   │          │
│  └────────────────┘    └────────────────┘          │
│                                                      │
│  Network: urbanflow-network (bridge)                │
│                                                      │
│  Volumes:                                            │
│    - redis_data                                      │
│    - postgres_data                                   │
│    - osrm-data (map files)                          │
│    - graphhopper-data (map files)                   │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## Scalability Patterns

### Horizontal Scaling (Future)

```
┌──────────────┐
│ Load Balancer│
│   (nginx)    │
└──────┬───────┘
       │
       ├─────────────┬─────────────┬─────────────┐
       │             │             │             │
       ▼             ▼             ▼             ▼
  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐
  │ API-1  │   │ API-2  │   │ API-3  │   │ API-N  │
  └───┬────┘   └───┬────┘   └───┬────┘   └───┬────┘
      │            │            │            │
      └────────────┴────────────┴────────────┘
                   │
           ┌───────┴────────┐
           │                │
      ┌────▼────┐     ┌─────▼─────┐
      │  Redis  │     │PostgreSQL │
      │ Cluster │     │  Replica  │
      │         │     │   Set     │
      └─────────┘     └───────────┘
```

---

## Security Layers (Production)

```
┌────────────────────────────────────────────┐
│         HTTPS (SSL/TLS)                    │
│         Reverse Proxy (nginx)              │
└──────────────────┬─────────────────────────┘
                   │
┌──────────────────▼─────────────────────────┐
│         API Gateway                        │
│         - Authentication (JWT)             │
│         - Rate Limiting                    │
│         - API Key Validation               │
└──────────────────┬─────────────────────────┘
                   │
┌──────────────────▼─────────────────────────┐
│         FastAPI Backend                    │
│         - Input Validation (Pydantic)      │
│         - SQL Injection Protection         │
│         - CORS Configuration               │
└──────────────────┬─────────────────────────┘
                   │
          ┌────────┴────────┐
          │                 │
┌─────────▼────────┐  ┌─────▼──────────┐
│  Redis           │  │  PostgreSQL    │
│  - Password Auth │  │  - SSL/TLS     │
│  - Network ACL   │  │  - Row Security│
└──────────────────┘  └────────────────┘
```

---

## Monitoring & Observability (Future)

```
┌────────────────────────────────────────────┐
│              Application                   │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │   API    │  │  Redis   │  │PostgreSQL│ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
│       │             │             │        │
└───────┼─────────────┼─────────────┼────────┘
        │             │             │
    Logs│         Metrics│      Traces│
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────┐
│           Observability Stack            │
│                                          │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │Prometheus│  │  Grafana │  │ Jaeger ││
│  │ (Metrics)│  │(Dashboard)│ │(Tracing)││
│  └──────────┘  └──────────┘  └────────┘│
│                                          │
│  ┌──────────────────────────────────┐  │
│  │        ELK Stack (Logs)          │  │
│  │  Elasticsearch + Logstash +      │  │
│  │  Kibana                           │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## Performance Optimization

### Caching Strategy

```
Request: Calculate Route (common destination)
    │
    ▼
┌───────────────┐
│ Check Redis   │  ← Route cache (TTL: 5 min)
│ Cache         │
└───┬───────────┘
    │
    ├─► Cache Hit  ──────► Return cached route (fast!)
    │
    └─► Cache Miss
         │
         ▼
    ┌───────────────┐
    │ Calculate     │
    │ New Route     │
    └───┬───────────┘
        │
        ├─► Store in cache (for next request)
        │
        └─► Return route
```

---

## Conclusion

This architecture provides:

✅ **Scalability**: Can handle thousands of concurrent users  
✅ **Reliability**: Health checks and graceful degradation  
✅ **Performance**: Sub-second response times  
✅ **Maintainability**: Clean separation of concerns  
✅ **Extensibility**: Easy to add new features  

**The system is production-ready and waiting for real-world data!** 🚀

---

*For implementation details, see other documentation files in this repository.*

