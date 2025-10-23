# 🧠 Smart Parking System - Zero Manual Setup!

## Overview

The Smart Parking system **automatically learns parking spots** by watching car behavior - **NO manual ROI drawing needed!**

## How It Works

### Phase 1: Learning (30 seconds)
1. ✅ Detects all cars using YOLO11x
2. ✅ Tracks each car's position over time
3. ✅ Identifies stationary cars (parked vehicles)
4. ✅ Clusters stationary positions into parking spots using DBSCAN algorithm
5. ✅ Saves learned spots to `learned_parking_spots.json`

### Phase 2: Monitoring (continuous)
1. ✅ Monitors learned parking spots for occupancy changes
2. ✅ Updates Redis with real-time data
3. ✅ Shows occupied (RED) vs free (GREEN) spots

---

## Quick Start

### 1. Run Smart Parking Detector

```bash
# Default: 30 second learning phase
python smart_parking.py

# Custom learning time (60 seconds)
python smart_parking.py --learning-time 60

# Use different config
python smart_parking.py --config config_parking.yaml
```

### 2. What You'll See

**During Learning (30s):**
```
🧠 LEARNING PARKING SPOTS...
Time remaining: 25.3s
Stationary observations: 145
```

**After Learning:**
```
✅ Learned 18 parking spots!
   Switching to monitoring mode...
💾 Saved learned spots to: learned_parking_spots.json

SMART PARKING MONITOR
Total Spots: 18
Occupied: 12
Available: 6
Occupancy: 66.7%
```

---

## Redis Data Published

### Summary Keys
```
urbanflow:smart_parking:total_spots       → 18
urbanflow:smart_parking:occupied_spots    → 12
urbanflow:smart_parking:available_spots   → 6
urbanflow:smart_parking:occupancy_rate    → 66.7
```

### Individual Spot Status
```
urbanflow:smart_parking:spot_1  → "occupied"
urbanflow:smart_parking:spot_2  → "free"
urbanflow:smart_parking:spot_3  → "occupied"
...
urbanflow:smart_parking:spot_18 → "free"
```

---

## Configuration Parameters

### In `smart_parking.py`:

```python
# Learning phase
learning_duration = 30  # seconds to learn parking spots

# Tracking parameters
iou_threshold = 0.3              # IoU for matching cars between frames
stationary_threshold = 20        # Max pixel movement for stationary
min_stationary_frames = 15       # Min frames to confirm parking spot

# Clustering parameters
cluster_eps = 80                 # Max distance between cars in same spot
cluster_min_samples = 3          # Min observations to form a parking spot
```

### Tuning Tips:

**If spots are too fragmented (too many small spots):**
- ⬆️ Increase `cluster_eps` (e.g., 100-120)
- ⬆️ Increase `cluster_min_samples` (e.g., 5-7)

**If spots are merged (multiple spots detected as one):**
- ⬇️ Decrease `cluster_eps` (e.g., 60-70)
- ⬇️ Decrease `cluster_min_samples` (e.g., 2-3)

**If not enough spots detected:**
- ⬆️ Increase `learning_duration` (e.g., 60 seconds)
- ⬇️ Decrease `min_stationary_frames` (e.g., 10)

---

## Learned Spots Format

`learned_parking_spots.json`:

```json
{
  "learned_at": "2025-10-23T12:30:45.123456",
  "video_source": "parcare.mp4",
  "spots": [
    {
      "id": 1,
      "center": [450, 320],
      "width": 120,
      "height": 180,
      "bbox": [390, 230, 510, 410]
    },
    {
      "id": 2,
      "center": [650, 315],
      "width": 125,
      "height": 185,
      "bbox": [587, 222, 712, 407]
    }
    // ... more spots
  ]
}
```

---

## Advantages vs Manual ROI Drawing

| Feature | Smart Parking | Manual ROI |
|---------|--------------|------------|
| Setup time | 30 seconds | 10-20 minutes |
| Manual work | Zero | Draw each spot |
| Accuracy | High | Depends on user |
| Adaptability | Auto-adjusts | Manual redraw |
| New cameras | Just run again | Redraw everything |

---

## Best Practices

### ✅ For Best Results:

1. **Use video with varied occupancy**
   - Mix of occupied and empty spots helps learning
   - Ideally 50-70% occupancy during learning phase

2. **Stable camera position**
   - Camera shouldn't move during operation
   - Fixed mounting is ideal

3. **Good lighting**
   - Clear visibility of cars
   - Consistent lighting conditions

4. **Longer learning for complex layouts**
   - Simple lots: 20-30 seconds
   - Complex/large lots: 60-90 seconds

### ⚠️ Limitations:

- **Requires car movement**: Need to see cars park/unpark during learning
- **Camera angle**: Works best with angled views (not extreme overhead)
- **Lighting changes**: May need re-learning if lighting drastically changes
- **Layout changes**: Need to re-run learning if parking layout is modified

---

## Comparison with Manual System

### Use Smart Parking When:
- ✅ You have multiple cameras to set up
- ✅ Parking layout may change over time
- ✅ You want zero manual configuration
- ✅ Camera angles are good (not extreme overhead)

### Use Manual ROI When:
- ✅ You need exact spot boundaries
- ✅ Parking spots have specific IDs/numbers
- ✅ Unusual spot shapes (not rectangular)
- ✅ Learning phase is difficult (static video, no movement)

---

## Troubleshooting

### Problem: No spots detected after learning

**Solution:**
- Check if cars are actually stationary in the video
- Increase `learning_duration` to 60+ seconds
- Decrease `min_stationary_frames` to 10

### Problem: Too many spots detected

**Solution:**
- Increase `cluster_eps` to merge nearby spots
- Increase `cluster_min_samples` for stricter clustering

### Problem: Spots in wrong locations

**Solution:**
- Ensure video shows typical parking behavior
- Use video with clear occupied/empty transitions
- Adjust `stationary_threshold` if cars are drifting

---

## Integration with Backend

The smart parking system publishes data in the same Redis format as the manual system, so **backend integration is identical**!

See: `BACKEND_INTEGRATION.md` for Redis key documentation.

---

## Future Enhancements

**Potential improvements:**
- 🔄 Continuous re-learning (adapt to layout changes)
- 📊 Occupancy heatmaps over time
- 🚗 Per-spot analytics (turnover rate, avg duration)
- 📱 Mobile app for spot reservation
- 🎯 Predictive occupancy (ML on historical data)

---

**Questions? Issues? Improvements?**

The system is designed to be fully automatic, but can be tuned for your specific use case!

