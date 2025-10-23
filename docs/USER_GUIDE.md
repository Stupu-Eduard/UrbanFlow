# 📘 UrbanFlowAI - User Guide

## Table of Contents
1. [Quick Reference](#quick-reference)
2. [Traffic Monitoring](#traffic-monitoring)
3. [Parking Detection](#parking-detection)
4. [Speed Tracking](#speed-tracking)
5. [Metrics & Analytics](#metrics--analytics)
6. [Multi-Video Setup](#multi-video-setup)

---

## Quick Reference

### Start System

```bash
# Backend
cd Heaven && docker-compose up -d

# Vision Engine (Traffic)
cd VisionEngine && python scripts/detector.py

# Vision Engine (Parking)
cd VisionEngine && python scripts/parking_detector.py --config config/config_parking.yaml
```

### Stop System

```bash
# Stop Vision Engine
Press 'q' in the video window or Ctrl+C

# Stop Backend
cd Heaven && docker-compose down
```

### Check Status

```bash
# Backend health
curl http://localhost:8000/health

# Redis keys
docker exec urbanflow-redis redis-cli KEYS "urbanflow:*"

# Metrics
cat VisionEngine/metrics/current_metrics.json
```

---

## Traffic Monitoring

### How It Works

1. **Detection:** YOLO detects vehicles (cars, trucks, buses)
2. **ROI Matching:** Checks which street each vehicle is in
3. **Congestion Scoring:** Calculates density (0-100%)
4. **Speed Tracking:** Measures vehicle speeds
5. **Publishing:** Sends data to Redis every frame

### Configuration

```yaml
traffic:
  streets:
    street_1:
      roi: [[x1,y1], [x2,y2], ...]  # Polygon points
      max_vehicles: 90               # Capacity threshold
      redis_key: urbanflow:traffic:street_1
```

### Congestion Levels

| Score | Level | Color | Description |
|-------|-------|-------|-------------|
| 0-40% | Low | 🟢 Green | Free-flowing traffic |
| 40-60% | Medium | 🟡 Yellow | Moderate congestion |
| 60-80% | High | 🟠 Orange | Heavy traffic |
| 80-100% | Critical | 🔴 Red | Gridlock |

### Drawing Street ROIs

```bash
python scripts/roi_editor.py --config config/config.yaml
```

**Tips:**
- Draw along street boundaries
- Include entire lane width
- Exclude intersections (overlap causes double-counting)
- Save with 'S' key

---

## Parking Detection

### Detection Modes

#### 1. Manual ROI Drawing (Most Accurate)

```bash
python scripts/roi_editor.py --config config/config_parking.yaml
```

**Best for:**
- Standard parking lots
- Marked parking spaces
- Defined layouts

**Steps:**
1. Draw polygons around each parking spot
2. Press 'G' for grid auto-generation
3. Save with 'S'

#### 2. Adaptive Detection (Automatic)

```bash
python scripts/parking_detector.py
```

**Best for:**
- Overhead camera views
- Unmarked parking areas
- Unknown layouts

**Features:**
- Tries multiple YOLO detection strategies
- Detects cars, then phones (for overhead), then small objects
- Automatically switches based on detection count
- Learns parking spots from car behavior

#### 3. Smart Occupancy Learning

The system can learn parking spots by observing:
- Stationary vehicle positions over time
- Clustering similar positions (DBSCAN)
- Inferring empty spots from grid patterns

**Configuration:**
```python
# In parking_detector.py
stationary_threshold = 5.0     # Max movement (pixels)
min_stationary_frames = 150    # ~10 seconds at 15 FPS
min_parking_duration = 300     # ~20 seconds to confirm
```

### Parking Metrics

**Published to Redis:**
```
urbanflow:parking:total_spots     → Total parking capacity
urbanflow:parking:occupied_spots  → Currently occupied
urbanflow:parking:available_spots → Currently available
urbanflow:parking:occupancy_rate  → Percentage (0-100)
urbanflow:parking:spot_{ID}       → "occupied" or "free"
```

### Parking Lot Types

| Type | Camera Angle | Best Method |
|------|--------------|-------------|
| Surface lot | Overhead (bird's eye) | Adaptive Detection |
| Street parking | Side view | Manual ROI |
| Underground | Overhead/angled | Manual ROI |
| Multi-level | Multiple cameras | Multi-Video Setup |

---

## Speed Tracking

### How It Works

1. **Object Tracking:** YOLO tracks vehicles across frames
2. **Position History:** Records center points + frame numbers
3. **Distance Calculation:** Measures pixel distance traveled
4. **Calibration:** Converts pixels to meters
5. **Speed Calculation:** distance (m) / time (s) × 3.6 = km/h

### Calibration

```bash
python scripts/calibrate_speed.py --config config/config.yaml
```

**Steps:**
1. Find a known distance in video (e.g., car length = 4.5m)
2. Click start point
3. Click end point
4. Enter real-world distance in meters
5. Script auto-updates config.yaml

**Example distances:**
- Car length: 4-5 meters
- Lane width: 3.5 meters
- Road marking (dashed): 3 meters
- Parking spot: 5 meters

### Speed Metrics

```yaml
speed_detection:
  pixels_per_meter: 31.3        # Calibrated conversion
  speed_limit_kmh: 50           # Threshold for alerts
  calibration_distance_m: 4.5   # Reference distance
  calibration_distance_px: 140.86  # Reference pixels
```

### Visualization

- **Green box:** Vehicle below speed limit
- **Red box:** Vehicle exceeding speed limit
- **Speed label:** Displays current speed (km/h)

---

## Metrics & Analytics

### Real-Time Metrics

**Location:** `VisionEngine/metrics/current_metrics.json`

**Updates:** Every frame (~15 times per second)

**Content:**
```json
{
  "timestamp": "2025-10-23T15:30:00",
  "parking": {
    "total_spots": 18,
    "occupied_spots": 11,
    "occupancy_rate": 61.1
  },
  "traffic": {
    "total_streets": 4,
    "average_congestion": 0.44,
    "street_details": {
      "street_1": {"congestion": 0.21, "level": "low"},
      "street_2": {"congestion": 0.55, "level": "medium"}
    }
  }
}
```

### Historical Metrics

**Location:** `VisionEngine/metrics/metrics_history.csv`

**Updates:** Every 5 seconds

**Columns:**
```csv
timestamp,parking_total,parking_occupied,parking_rate,traffic_avg_congestion
2025-10-23 15:30:00,18,11,61.1,44.3
2025-10-23 15:30:05,18,12,66.7,45.2
...
```

### Metrics Analysis

**View recent metrics:**
```bash
tail -20 VisionEngine/metrics/metrics_history.csv
```

**Calculate averages:**
```python
import pandas as pd
df = pd.read_csv('VisionEngine/metrics/metrics_history.csv')
print(f"Avg Parking Occupancy: {df['parking_rate'].mean():.1f}%")
print(f"Avg Traffic Congestion: {df['traffic_avg_congestion'].mean():.1f}%")
```

**Export for visualization:**
```bash
# Convert to JSON
python -c "import pandas as pd; pd.read_csv('metrics_history.csv').to_json('metrics.json', orient='records')"
```

---

## Multi-Video Setup

### Why Multiple Videos?

- **Separate feeds:** Traffic intersection + Parking lot
- **Different ROIs:** Streets vs parking spots
- **Independent processing:** Run simultaneously
- **Different configs:** Custom settings per video

### Configuration Structure

```
VisionEngine/
├── config/
│   ├── config.yaml           # Traffic video
│   ├── config_parking.yaml   # Parking video
│   └── config_overhead.yaml  # Overhead parking
└── scripts/
    ├── detector.py           # Processes any config
    └── parking_detector.py   # Parking-specific features
```

### Running Multiple Feeds

**Terminal 1: Traffic**
```bash
cd VisionEngine
python scripts/detector.py --config config/config.yaml
```

**Terminal 2: Parking**
```bash
cd VisionEngine
python scripts/parking_detector.py --config config/config_parking.yaml
```

**Terminal 3: Backend**
```bash
cd Heaven
docker-compose up
```

### Redis Key Isolation

Each video uses different Redis keys:

**Traffic (config.yaml):**
```
urbanflow:traffic:street_1
urbanflow:traffic:street_2
```

**Parking (config_parking.yaml):**
```
urbanflow:parking:total_spots
urbanflow:parking:spot_A1
```

No conflicts! Both publish to same Redis, different keys.

### Config Per Video

**Traffic video (config.yaml):**
```yaml
video:
  source: traffic_video.mp4
traffic:
  streets:
    street_1: { roi: [...], max_vehicles: 90 }
parking:
  spots: {}  # No parking spots for traffic video
```

**Parking video (config_parking.yaml):**
```yaml
video:
  source: parking_video.mp4
traffic:
  streets: {}  # No streets for parking video
parking:
  spots:
    SPOT_A1: { roi: [...] }
    SPOT_A2: { roi: [...] }
```

### ROI Management

**Edit traffic ROIs:**
```bash
python scripts/roi_editor.py --config config/config.yaml
```

**Edit parking ROIs:**
```bash
python scripts/roi_editor.py --config config/config_parking.yaml
```

ROIs are saved separately in each config file.

---

## Advanced Features

### Emergency Vehicle Detection

Currently disabled by default. To enable:

```yaml
emergency:
  vehicle_class: 7  # Truck (placeholder for emergency)
  track_all: true
  redis_key_prefix: urbanflow:emergency:truck_
```

### Custom YOLO Classes

```yaml
model:
  classes_to_detect:
    - 2  # car
    - 3  # motorcycle  
    - 5  # bus
    - 7  # truck
```

**Full COCO classes:**
0=person, 1=bicycle, 2=car, 3=motorcycle, 5=bus, 7=truck

### Performance Optimization

**GPU Acceleration:**
```yaml
model:
  device: cuda  # Use NVIDIA GPU
```

**Frame Skipping:**
```yaml
video:
  target_fps: 5  # Process fewer frames
```

**Smaller Model:**
```yaml
model:
  weights: yolo11n.pt  # Nano (fastest)
  # Or: yolo11s.pt (small)
  # Or: yolo11m.pt (medium)
  # Or: yolo11l.pt (large)
  # Or: yolo11x.pt (extra large, current)
```

---

## Tips & Best Practices

### For Traffic Monitoring

✅ **Do:**
- Draw ROIs along street boundaries
- Set realistic `max_vehicles` based on observation
- Calibrate speed for accurate measurements
- Use high-quality video (1080p+)

❌ **Don't:**
- Overlap ROIs (causes double-counting)
- Set confidence too low (<0.05, many false positives)
- Use videos with severe occlusion

### For Parking Detection

✅ **Do:**
- Use overhead camera when possible
- Draw tight ROIs around parking spots
- Use adaptive detector for unknown layouts
- Verify spot count matches reality

❌ **Don't:**
- Include walkways in parking ROIs
- Mix street parking with lot parking
- Use extremely low resolution

### For Speed Tracking

✅ **Do:**
- Calibrate with known distance
- Use car length (~4.5m) for reference
- Verify speeds with real observation
- Use perpendicular camera angle

❌ **Don't:**
- Skip calibration (speeds will be wrong)
- Use extreme camera angles
- Expect 100% accuracy (±5 km/h typical)

---

## Keyboard Controls

**During Video Playback:**
- `Q` - Quit detector
- `Space` - Pause/Resume (if implemented)

**In ROI Editor:**
- `Left Click` - Add point to polygon
- `Right Click` - Close current polygon
- `R` - Toggle rectangle mode
- `G` - Generate parking grid
- `U` - Undo last point
- `C` - Clear current ROI
- `S` - Save ROIs
- `Q` - Quit editor

---

## Troubleshooting

**Low detection count?**
- Lower `confidence` threshold
- Use larger YOLO model (`yolo11x.pt`)
- Improve video quality
- Check camera angle

**Wrong parking occupancy?**
- Verify ROIs cover full parking spots
- Check for ROI overlap
- Try adaptive detector
- Manually draw problem areas

**Inaccurate speeds?**
- Re-run calibration tool
- Ensure perpendicular camera view
- Check FPS is correct
- Verify `pixels_per_meter` value

**High CPU usage?**
- Lower `target_fps`
- Use smaller YOLO model
- Enable GPU (`device: cuda`)
- Reduce video resolution

---

**For setup instructions, see:** `SETUP_GUIDE.md`  
**For frontend development, see:** `FOR_DEVELOPERS.md`

