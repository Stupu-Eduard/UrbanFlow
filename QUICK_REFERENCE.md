# UrbanFlowAI - Quick Reference for Backend

## 🔌 Connect to Redis

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
```

---

## 📊 Read Data

### Traffic Density (0.0 to 1.0)
```python
density = float(r.get("urbanflow:traffic:street_1") or 0.0)
# 0.0 = empty, 0.5 = 50% congested, 1.0 = 100% congested
```

### Parking Status ("occupied" or "free")
```python
status = r.get("urbanflow:parking:SPOT_A1")
# Returns: "occupied" or "free"
```

### Emergency Vehicles (JSON)
```python
import json
keys = r.keys("urbanflow:emergency:truck_*")
for key in keys:
    vehicle = json.loads(r.get(key))
    print(vehicle['location'])  # [x, y] coordinates
```

---

## 📋 Redis Keys

| Service | Key | Value | Example |
|---------|-----|-------|---------|
| **Traffic** | `urbanflow:traffic:street_1` | `"0.82"` | 82% congested |
| **Parking** | `urbanflow:parking:SPOT_A1` | `"occupied"` | Spot is taken |
| **Emergency** | `urbanflow:emergency:truck_01` | `{"id":"truck_01","location":[640,320]}` | Truck detected |

---

## ⚡ That's It!

1. Install: `pip install redis`
2. Start Redis: `sudo systemctl start redis-server`
3. Vision Engineer runs: `python detector.py`
4. You read from Redis using keys above

**Full documentation:** See `BACKEND_INTEGRATION.md`

