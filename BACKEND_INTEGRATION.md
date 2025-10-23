# UrbanFlowAI - Backend Integration Guide

> **For Backend Engineers**: How to consume real-time data from the Vision Engine

---

## 📡 Redis Connection

### Connection Details:
```python
import redis

r = redis.Redis(
    host='localhost',    # Change if Redis is on different server
    port=6379,
    db=0,
    decode_responses=True  # Important: Get strings instead of bytes
)
```

---

## 🚦 Data Schema

### 1️⃣ **Traffic Monitoring** (Street Congestion)

**Redis Key Format:** `urbanflow:traffic:{street_name}`

**Data Type:** String (float as string)

**Value Range:** `"0.0"` to `"1.0"` (density percentage)

**Update Frequency:** 10-15 times per second (real-time)

**Example:**
```python
# Read traffic density
density = float(r.get("urbanflow:traffic:street_1") or 0.0)

# density = 0.0  → Empty street
# density = 0.5  → 50% congestion
# density = 1.0  → 100% congestion (max_vehicles reached)
```

**Available Keys:**
- `urbanflow:traffic:street_1` (main intersection)
- Add more as Vision Engineer defines more street ROIs

**TTL:** No expiration (persists until updated)

---

### 2️⃣ **Smart Parking** (Spot Occupancy + Lot Summary)

#### **A. Individual Parking Spots**

**Redis Key Format:** `urbanflow:parking:{spot_name}`

**Data Type:** String

**Value:** `"occupied"` or `"free"`

**Update Frequency:** 10-15 times per second (real-time)

**Example:**
```python
# Read parking spot status
spot_a1 = r.get("urbanflow:parking:SPOT_A1")  # Returns "occupied" or "free"

if spot_a1 == "occupied":
    print("Parking spot A1 is taken")
elif spot_a1 == "free":
    print("Parking spot A1 is available")
```

**Available Keys:**
- `urbanflow:parking:SPOT_A1`
- `urbanflow:parking:SPOT_A2`
- Add more as Vision Engineer defines more parking ROIs

**TTL:** No expiration (persists until updated)

---

#### **B. Parking Lot Summary** 🆕

**NEW FEATURE:** Get overall parking lot statistics!

**Redis Keys:**

| Key | Type | Value | Description |
|-----|------|-------|-------------|
| `urbanflow:parking:total_spots` | String | `"20"` | Total parking spots defined |
| `urbanflow:parking:occupied_spots` | String | `"15"` | Number of occupied spots |
| `urbanflow:parking:available_spots` | String | `"5"` | Number of free spots |
| `urbanflow:parking:occupancy_rate` | String | `"75.0"` | Occupancy percentage |

**Example:**
```python
# Get parking lot summary
total = int(r.get("urbanflow:parking:total_spots") or 0)
occupied = int(r.get("urbanflow:parking:occupied_spots") or 0)
available = int(r.get("urbanflow:parking:available_spots") or 0)
occupancy = float(r.get("urbanflow:parking:occupancy_rate") or 0)

print(f"Parking Lot Status:")
print(f"  Total: {total} spots")
print(f"  Occupied: {occupied} spots")
print(f"  Available: {available} spots")
print(f"  Occupancy: {occupancy}%")

# Output:
# Parking Lot Status:
#   Total: 20 spots
#   Occupied: 15 spots
#   Available: 5 spots
#   Occupancy: 75.0%
```

**Update Frequency:** 10-15 times per second (real-time)

**TTL:** No expiration (persists until updated)

---

### 3️⃣ **Emergency Vehicle Tracking**

**Redis Key Format:** `urbanflow:emergency:truck_{id}`

**Data Type:** String (JSON)

**Value Format:**
```json
{
  "id": "truck_01",
  "location": [x, y],
  "bbox": [x1, y1, x2, y2],
  "timestamp": 1234567890.123
}
```

**Update Frequency:** 10-15 times per second (real-time)

**TTL:** 5 seconds (auto-expires if vehicle leaves frame)

**Example:**
```python
import json

# Get all emergency vehicles currently detected
emergency_keys = r.keys("urbanflow:emergency:truck_*")

for key in emergency_keys:
    data = json.loads(r.get(key))
    print(f"Emergency vehicle {data['id']} at location {data['location']}")
    
# Output:
# Emergency vehicle truck_01 at location [640, 320]
# Emergency vehicle truck_02 at location [800, 450]
```

**Note:** Keys automatically expire after 5 seconds if vehicle is no longer detected.

---

## 🔄 Complete Integration Example

```python
import redis
import json
import time

class UrbanFlowBackend:
    def __init__(self):
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
    
    def get_traffic_density(self, street_name="street_1"):
        """Get current traffic density for a street."""
        key = f"urbanflow:traffic:{street_name}"
        density = self.redis.get(key)
        return float(density) if density else 0.0
    
    def get_parking_status(self, spot_name):
        """Get parking spot status (occupied/free)."""
        key = f"urbanflow:parking:{spot_name}"
        status = self.redis.get(key)
        return status if status else "unknown"
    
    def get_all_parking_spots(self):
        """Get status of all parking spots."""
        keys = self.redis.keys("urbanflow:parking:*")
        spots = {}
        for key in keys:
            spot_name = key.split(":")[-1]
            spots[spot_name] = self.redis.get(key)
        return spots
    
    def get_emergency_vehicles(self):
        """Get all currently detected emergency vehicles."""
        keys = self.redis.keys("urbanflow:emergency:truck_*")
        vehicles = []
        for key in keys:
            data = self.redis.get(key)
            if data:
                vehicles.append(json.loads(data))
        return vehicles
    
    def get_full_system_state(self):
        """Get complete snapshot of entire system."""
        return {
            "traffic": {
                "street_1": self.get_traffic_density("street_1")
            },
            "parking": self.get_all_parking_spots(),
            "emergency": self.get_emergency_vehicles(),
            "timestamp": time.time()
        }


# Usage Example
if __name__ == "__main__":
    backend = UrbanFlowBackend()
    
    # Real-time monitoring loop
    while True:
        state = backend.get_full_system_state()
        
        print(f"\n{'='*60}")
        print(f"System State @ {time.strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        # Traffic
        print(f"\n🚗 Traffic:")
        density = state['traffic']['street_1']
        print(f"  Street 1: {density:.0%} congested")
        
        # Parking
        print(f"\n🅿️  Parking:")
        for spot, status in state['parking'].items():
            emoji = "🔴" if status == "occupied" else "🟢"
            print(f"  {emoji} {spot}: {status}")
        
        # Emergency
        print(f"\n🚑 Emergency Vehicles:")
        if state['emergency']:
            for vehicle in state['emergency']:
                print(f"  • {vehicle['id']} at {vehicle['location']}")
        else:
            print(f"  None detected")
        
        time.sleep(1)  # Update every second
```

---

## 📊 Expected Data Output Examples

### Scenario 1: Low Traffic, Parking Available
```json
{
  "traffic": {
    "street_1": 0.15
  },
  "parking": {
    "SPOT_A1": "free",
    "SPOT_A2": "free"
  },
  "emergency": [],
  "timestamp": 1729630800.123
}
```

### Scenario 2: High Traffic, Parking Full, Emergency Vehicle
```json
{
  "traffic": {
    "street_1": 0.89
  },
  "parking": {
    "SPOT_A1": "occupied",
    "SPOT_A2": "occupied"
  },
  "emergency": [
    {
      "id": "truck_01",
      "location": [640, 320],
      "bbox": [600, 280, 680, 360],
      "timestamp": 1729630800.456
    }
  ],
  "timestamp": 1729630800.456
}
```

---

## 🔧 Configuration Values

**Vision Engine is configured with:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| `max_vehicles` | 90 | Max cars in intersection = 100% density |
| `target_fps` | 15 | Processing speed (updates/sec) |
| `confidence` | 0.15 | YOLO detection threshold (adjustable) |
| `emergency_class` | 7 (truck) | COCO class for emergency vehicles |

**To request changes:** Ask Vision Engineer to update `config.yaml`

---

## ⚙️ System Requirements (Backend Side)

### Install Redis Client:
```bash
pip install redis
```

### Check Redis Connection:
```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.ping()  # Should return True
```

### Install Redis Server (if needed):
```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis

# Windows (WSL2)
sudo service redis-server start
```

---

## 🚀 Deployment Workflow

### Development Phase:
1. **Vision Engineer** runs: `python detector.py` (processes video → publishes to Redis)
2. **Backend Engineer** runs: Your app (reads from Redis)
3. Both systems run on `localhost:6379`

### Production Phase:
**Option A - Same Server:**
- Both services run on same machine
- Redis at `localhost:6379`

**Option B - Separate Servers:**
- Vision Engine on GPU server (publishes to Redis)
- Backend on app server (reads from Redis)
- Update connection: `host='vision-server-ip'`

---

## 🐛 Troubleshooting

### "Connection refused" Error:
```python
# Check if Redis is running
redis-cli ping  # Should return PONG
```

### No Data in Redis:
```python
# Check if Vision Engine is running
# You should see this in Vision Engineer's terminal:
# "✓ Connected to Redis at localhost:6379"
```

### Stale Data:
```python
# Emergency vehicle keys expire after 5 seconds
# Other keys update 10-15 times per second
# If data seems frozen, Vision Engine may have crashed
```

---

## 📞 Communication with Vision Engineer

### Request Changes:
- **Add more streets:** "Please add street_2 ROI"
- **Add more parking:** "Please add SPOT_A3, SPOT_A4"
- **Adjust sensitivity:** "Too many false positives, increase confidence to 0.20"
- **Adjust max_vehicles:** "Set max_vehicles to 120 for street_1"

### Provide Feedback:
- "Traffic density seems too low/high"
- "Parking detection not accurate for spot X"
- "Need emergency vehicles to include buses too"

---

## 📝 Redis Key Summary

| Service | Key Pattern | Type | Value | TTL |
|---------|-------------|------|-------|-----|
| Traffic | `urbanflow:traffic:{street_name}` | String | `"0.0"` - `"1.0"` | None |
| Parking | `urbanflow:parking:{spot_name}` | String | `"occupied"` / `"free"` | None |
| Emergency | `urbanflow:emergency:truck_{id}` | String (JSON) | `{"id", "location", "bbox", "timestamp"}` | 5s |

---

## ✅ Integration Checklist

- [ ] Redis installed and running (`redis-cli ping`)
- [ ] Redis Python client installed (`pip install redis`)
- [ ] Vision Engine running (`python detector.py`)
- [ ] Can read traffic data: `r.get("urbanflow:traffic:street_1")`
- [ ] Can read parking data: `r.get("urbanflow:parking:SPOT_A1")`
- [ ] Can read emergency data: `r.keys("urbanflow:emergency:*")`
- [ ] Backend app consuming data successfully
- [ ] Coordinated testing with Vision Engineer

---

## 🎯 Final Notes

**Data Ownership:**
- Vision Engine = **Data Producer** (writes to Redis)
- Backend = **Data Consumer** (reads from Redis)

**Performance:**
- Updates: 10-15 FPS (very responsive)
- Latency: <100ms from detection to Redis
- Redis overhead: Minimal (simple key-value operations)

**Scalability:**
- Single video stream: Current setup
- Multiple cameras: Vision Engineer can add more ROIs or run multiple detector instances
- Each street/parking spot = independent Redis key

---

**Ready to integrate? Contact Vision Engineer if you need:**
- More ROIs defined
- Different data formats
- Higher/lower update rates
- Additional vehicle classes tracked

**Built with UrbanFlowAI Vision Engine v1.0** 🚀

