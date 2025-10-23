# 📜 UrbanFlowAI Data Contracts

**The "Language" Between All Roles**

This document defines the precise data format and protocols that all team members must follow.

---

## Contract Overview

```
┌──────────────────────────────────────────────────────────┐
│                    DATA FLOW                             │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Role 1 (AI Vision)                                      │
│       │                                                   │
│       ├─► Redis: "traffic:street_1" = "0.75"            │
│       ├─► Redis: "parking:zone_A:A1" = "free"           │
│       └─► Redis: "emergency:amb_001" = {...}            │
│                                                           │
│           ▼                                               │
│                                                           │
│  Role 2 (Backend - THIS SYSTEM)                          │
│       │                                                   │
│       ├─► Reads from Redis                               │
│       ├─► Combines with PostgreSQL data                  │
│       └─► Exposes REST API                               │
│                                                           │
│           ▼                                               │
│                                                           │
│  Role 3 (Frontend)                                       │
│       │                                                   │
│       ├─► Calls GET /api/v1/status/live                  │
│       └─► Calls POST /api/v1/route/calculate             │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## Part 1: INPUT Contract (Role 1 → Role 2)

### For AI Vision Engineer (Role 1)

You are responsible for populating Redis with real-time data. The backend (Role 2) will read this data to provide intelligence.

### Connection Details

```
Host: localhost (or 'redis' in Docker)
Port: 6379
Database: 0
Protocol: Redis
```

### Contract 1.1: Traffic Congestion Data

**Purpose**: Report how congested each street is.

**Format** (ACTUAL FROM VISION ENGINE):
```
Key Pattern: "urbanflow:traffic:{street_name}"
Value Type:  String (representing a float)
Value Range: "0.0" to "1.0"
```

**Meaning**:
- `0.0` = Free flowing traffic (0 vehicles detected)
- `0.5` = 50% congestion (45/90 vehicles if max_vehicles=90)
- `1.0` = 100% congestion (max_vehicles reached)

**Example - Python**:
```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Report that street_1 is 75% congested
r.set('urbanflow:traffic:street_1', '0.75')

# Report that street_2 is free
r.set('urbanflow:traffic:street_2', '0.1')

# Report critical congestion
r.set('urbanflow:traffic:street_3', '0.95')
```

**Example - JavaScript/Node.js**:
```javascript
const redis = require('redis');
const client = redis.createClient();

await client.connect();

// Set traffic data
await client.set('traffic:street_1', '0.75');
await client.set('traffic:street_2', '0.1');
```

**Street IDs**:
You'll get these from the backend team. They match the database.

**Update Frequency**:
Update every 5-10 seconds for real-time accuracy.

**Expiration**:
No expiration needed - just overwrite with new values.

---

### Contract 1.2: Parking Spot Status

**Purpose**: Report if parking spots are free or occupied.

**Format** (ACTUAL FROM VISION ENGINE):
```
Key Pattern: "urbanflow:parking:{spot_name}"
Value Type:  String (enum)
Value Options: "free" | "occupied"
```

**Example - Python**:
```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Mark spots as free or occupied (Vision Engine format)
r.set('urbanflow:parking:SPOT_A1', 'free')
r.set('urbanflow:parking:SPOT_A2', 'occupied')
r.set('urbanflow:parking:SPOT_A3', 'free')

# More spots
r.set('urbanflow:parking:SPOT_B1', 'occupied')
r.set('urbanflow:parking:SPOT_B2', 'free')
```

**Spot IDs**:
Format: `SPOT_{ZONE}{NUMBER}`
- Zone A: `SPOT_A1`, `SPOT_A2`, ... `SPOT_A50`
- Zone B: `SPOT_B1`, `SPOT_B2`, ... `SPOT_B30`

**Update Frequency**:
10-15 times per second (real-time from Vision Engine)

**Batch Updates**:
```python
# Efficient batch update
pipeline = r.pipeline()
for i in range(1, 51):
    status = 'free' if spot_is_free(i) else 'occupied'
    pipeline.set(f'urbanflow:parking:SPOT_A{i}', status)
pipeline.execute()
```

---

### Contract 1.3: Emergency Vehicle Location

**Purpose**: Track real-time location of emergency vehicles.

**Format** (ACTUAL FROM VISION ENGINE):
```
Key Pattern: "urbanflow:emergency:truck_{id}"
Value Type:  JSON String
TTL: 5 seconds (auto-expires)
```

**JSON Schema**:
```json
{
  "id": "truck_01",
  "location": [x, y],               // Pixel coordinates [float, float]
  "bbox": [x1, y1, x2, y2],        // Bounding box [float, float, float, float]
  "timestamp": 1234567890.123       // Unix timestamp (float)
}
```

**Example - Python**:
```python
import redis
import json
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Update emergency vehicle location (Vision Engine format)
vehicle_data = {
    "id": "truck_01",
    "location": [640, 320],          # Pixel coordinates (x, y)
    "bbox": [600, 280, 680, 360],    # Bounding box [x1, y1, x2, y2]
    "timestamp": time.time()          # Current timestamp
}

# IMPORTANT: Use setex with 5 second TTL
r.setex('urbanflow:emergency:truck_01', 5, json.dumps(vehicle_data))
```

**Key Notes**:
- Coordinates are in **pixels** (Vision Engine detects from video)
- Backend converts to GPS coordinates for routing
- **TTL of 5 seconds** - keys auto-expire if vehicle leaves frame
- Update frequency: 10-15 times per second while vehicle is visible

**Example - JavaScript**:
```javascript
const vehicleData = {
  vehicle_id: "amb_001",
  latitude: 40.7489,
  longitude: -73.9852,
  heading: 45.0,
  speed: 60.0,
  status: "responding",
  last_updated: new Date().toISOString()
};

await client.set('emergency:amb_001', JSON.stringify(vehicleData));
```

**Vehicle IDs**:
Use consistent IDs like `amb_001`, `fire_001`, `police_001`.

**Update Frequency**:
Every 3-5 seconds while vehicle is active.

**Remove When Idle**:
```python
# Remove vehicle from tracking when no longer active
r.delete('emergency:amb_001')
```

---

### Testing Your Integration (Role 1)

**1. Check Redis Connection**:
```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
print(r.ping())  # Should return True
```

**2. Verify Data Was Written**:
```python
# Write data
r.set('traffic:street_1', '0.75')

# Read it back
value = r.get('traffic:street_1')
print(value)  # Should print "0.75"
```

**3. Check Backend Can Read It**:
```bash
# Use the backend's admin endpoint
curl http://localhost:8000/api/v1/admin/redis-status
```

This will show what data the backend sees in Redis.

---

## Part 2: OUTPUT Contract (Role 2 → Role 3)

### For Frontend Engineer (Role 3)

The backend exposes a clean REST API. You don't need to know about Redis or PostgreSQL.

### Connection Details

```
Base URL: http://localhost:8000 (development)
Protocol: HTTP/REST
Format: JSON
```

### Contract 2.1: Live Status Endpoint

**Endpoint**: `GET /api/v1/status/live`

**Purpose**: Get a complete real-time snapshot of the city.

**Response Schema**: See `API_DOCUMENTATION.md` for full details.

**Key Points for Frontend**:
- Call every 5-10 seconds for live updates
- Response includes everything: traffic, parking, emergencies
- All coordinates in GeoJSON format: `[longitude, latitude]`
- Congestion levels are pre-calculated (low/medium/high/critical)

**Quick Reference**:
```javascript
const response = await fetch('http://localhost:8000/api/v1/status/live');
const data = await response.json();

// Access data
data.streets           // Array of streets with traffic
data.parking_zones     // Array of parking zones
data.emergency_vehicles // Array of active emergency vehicles
data.average_congestion // City-wide average (0.0 to 1.0)
data.total_free_spots  // Total available parking
```

### Contract 2.2: Route Calculation Endpoint

**Endpoint**: `POST /api/v1/route/calculate`

**Purpose**: Calculate intelligent routes.

**Request Schema**:
```typescript
interface RouteRequest {
  start: {
    latitude: number;   // -90 to 90
    longitude: number;  // -180 to 180
  };
  end: {
    latitude: number;
    longitude: number;
  };
  mode: "citizen" | "emergency" | "smartpark";
  vehicle_id?: string;  // Required for emergency mode
}
```

**Response Contains**:
- Full route coordinates for map display
- Turn-by-turn instructions
- Distance and duration
- (Emergency mode) List of avoided congested streets

---

## Data Validation Rules

### Role 1 Must Ensure:

1. **Traffic Congestion**:
   - Values are strings representing floats: "0.0" to "1.0"
   - Invalid: `r.set('traffic:street_1', '1.5')` ❌
   - Valid: `r.set('traffic:street_1', '0.95')` ✅

2. **Parking Status**:
   - Values are exactly "free" or "occupied" (lowercase)
   - Invalid: `r.set('parking:zone_A:A1', 'Free')` ❌
   - Valid: `r.set('parking:zone_A:A1', 'free')` ✅

3. **Emergency Vehicles**:
   - Must be valid JSON
   - Must include required fields: vehicle_id, latitude, longitude, status, last_updated
   - Latitude: -90 to 90
   - Longitude: -180 to 180

### Role 3 Can Expect:

1. **Consistent Coordinate Format**:
   - Always `[longitude, latitude]` (GeoJSON format)
   - Never `[latitude, longitude]`

2. **Timestamps**:
   - Always ISO 8601 format with 'Z' suffix
   - Example: "2024-01-15T10:30:00.000Z"

3. **Enum Values**:
   - Congestion level: "low", "medium", "high", "critical"
   - Parking status: "free", "occupied", "unknown"
   - Vehicle status: "active", "idle", "responding"
   - Routing mode: "citizen", "emergency", "smartpark"

---

## Error Handling

### Role 1: What Happens If You Provide Bad Data?

The backend is resilient:
- Invalid congestion scores → Treated as 0.0 (no congestion)
- Invalid parking status → Treated as "unknown"
- Invalid JSON for emergency → Ignored (not displayed)
- Missing data → Defaults used

**But you should still provide correct data!**

### Role 3: What Happens If The API Fails?

```javascript
try {
  const response = await fetch('http://localhost:8000/api/v1/status/live');
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const data = await response.json();
  updateDashboard(data);
} catch (error) {
  console.error('API call failed:', error);
  // Show cached data or error message to user
  showErrorMessage('Unable to fetch live data');
}
```

---

## Sample Integration: Complete Flow

### 1. Role 1 Writes Data

```python
import redis
import json
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Write traffic data
r.set('traffic:street_1', '0.3')  # Low congestion
r.set('traffic:street_2', '0.8')  # High congestion

# Write parking data
r.set('parking:zone_A:A1', 'free')
r.set('parking:zone_A:A2', 'occupied')

# Write emergency vehicle
vehicle = {
    "vehicle_id": "amb_001",
    "latitude": 40.7489,
    "longitude": -73.9852,
    "status": "responding",
    "last_updated": datetime.utcnow().isoformat() + "Z"
}
r.set('emergency:amb_001', json.dumps(vehicle))

print("✓ Data written to Redis")
```

### 2. Role 2 Processes Data

(Automatic - this system does this)

The backend:
- Reads Redis data
- Combines with PostgreSQL (street names, parking zones)
- Calculates averages and summaries
- Exposes via REST API

### 3. Role 3 Consumes Data

```javascript
async function updateDashboard() {
  // Fetch live status
  const response = await fetch('http://localhost:8000/api/v1/status/live');
  const data = await response.json();
  
  // Use the data
  console.log('Average congestion:', data.average_congestion);
  
  // Display on map
  data.streets.forEach(street => {
    if (street.congestion_level === 'high') {
      drawRedStreet(street.coordinates);
    } else if (street.congestion_level === 'medium') {
      drawYellowStreet(street.coordinates);
    } else {
      drawGreenStreet(street.coordinates);
    }
  });
  
  // Show parking availability
  data.parking_zones.forEach(zone => {
    updateParkingWidget(zone.zone_name, zone.free_spots);
  });
  
  // Alert for emergencies
  if (data.active_emergencies > 0) {
    showEmergencyAlert(data.emergency_vehicles);
  }
}

// Update every 10 seconds
setInterval(updateDashboard, 10000);
```

---

## Verification Checklist

### Role 1 Checklist:
- [ ] Redis connection working (`r.ping()` returns True)
- [ ] Traffic data format correct (string "0.0" to "1.0")
- [ ] Parking data format correct ("free" or "occupied")
- [ ] Emergency vehicle JSON is valid
- [ ] Backend can see my data (`curl .../admin/redis-status`)

### Role 3 Checklist:
- [ ] API health check works (`GET /health`)
- [ ] Live status returns data (`GET /api/v1/status/live`)
- [ ] Route calculation works (`POST /api/v1/route/calculate`)
- [ ] Coordinates display correctly on map
- [ ] Error handling implemented

---

## Communication Protocol

### When Role 1 Needs to Change Data Format:

1. Propose change to Role 2 (Backend team)
2. Role 2 updates this contract document
3. Role 2 updates backend code
4. Role 2 notifies Role 3 if API changes
5. All roles implement changes together

### When Role 3 Needs New Data:

1. Request from Role 2 (Backend team)
2. Role 2 checks if data is available from Role 1
3. If not, Role 2 requests from Role 1
4. Role 2 exposes new API endpoint
5. Role 2 updates this contract document

---

## Quick Reference Tables

### Redis Key Patterns (Role 1)

| Purpose | Key Pattern | Value Example |
|---------|-------------|---------------|
| Traffic | `traffic:{street_id}` | `"0.75"` |
| Parking | `parking:{zone_id}:{spot_id}` | `"free"` |
| Emergency | `emergency:{vehicle_id}` | `{...JSON...}` |

### API Endpoints (Role 3)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | System health |
| `/api/v1/status/live` | GET | Live city data |
| `/api/v1/route/calculate` | POST | Calculate route |

---

## Support

- **Contract Questions**: Contact Role 2 (Backend team)
- **Redis Issues**: See Redis documentation
- **API Issues**: See `API_DOCUMENTATION.md`

---

**This contract is the "constitution" of UrbanFlowAI. Follow it strictly!** 📜✨

