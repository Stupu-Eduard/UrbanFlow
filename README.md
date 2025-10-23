# UrbanFlowAI - Vision Engine 👁️

> **The "Eyes" of the System** - Real-time computer vision engine that transforms video feeds into actionable urban mobility data.

---

## 🎯 What This Does

This is the **perception layer** for UrbanFlowAI. It processes city camera feeds (simulated via MP4) and outputs structured, real-time data to Redis for three critical urban services:

| Service | Input | Output | Format |
|---------|-------|--------|--------|
| 🚑 **Emergency Mode** | Truck detection (ambulance stand-in) | Location tracking | `{"urbanflow:emergency:truck_01": '{"id": "truck_01", "location": [x, y]}'}` |
| 🚗 **Traffic Monitoring** | Vehicle count in street ROIs | Congestion density (0.0-1.0) | `{"urbanflow:traffic:street_1": 0.82}` |
| 🅿️ **Smart Parking** | Car presence in parking spots | Spot status | `{"urbanflow:parking:SPOT_A1": "occupied"}` |

---

## 🚀 Quick Start

### 1️⃣ Setup Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Note:** First run will auto-download YOLOv8s weights (~22MB)

### 2️⃣ Get Your Video

Download a traffic video from YouTube (e.g., "city traffic 1080p"):

```bash
# Create videos directory
mkdir -p videos

# Download using yt-dlp (if you have it)
yt-dlp -f "best[height<=1080]" -o "videos/city_traffic.mp4" <YOUTUBE_URL>

# Or manually download and place in videos/city_traffic.mp4
```

Update `config.yaml`:
```yaml
video:
  source: "videos/city_traffic.mp4"
```

### 3️⃣ Define Regions of Interest (ROIs)

Use the interactive ROI editor to draw zones on your video:

```bash
python roi_editor.py
```

**Instructions:**
- **Left-click** to add polygon points
- **Press 'c'** to complete current ROI
- **Press 'r'** to reset current ROI
- **Press 's'** to save all ROIs to `config.yaml`
- **Press 'q'** to quit

**ROI Naming Convention:**
- Streets: `street_1`, `street_2`, etc.
- Parking: `SPOT_A1`, `SPOT_A2`, etc.

### 4️⃣ Configure Traffic Thresholds

After defining ROIs, update `max_vehicles` in `config.yaml` based on your video:

```yaml
traffic:
  streets:
    street_1:
      roi: [[x1,y1], [x2,y2], ...]  # Auto-filled by roi_editor
      max_vehicles: 20  # ← UPDATE THIS: How many cars = 100% congestion?
```

**How to determine this:**
- Watch your video
- Count max vehicles you see in that street ROI during heavy traffic
- Set that as `max_vehicles`

### 5️⃣ Start Detection

```bash
python detector.py
```

**Expected Output:**
```
======================================================================
 UrbanFlowAI - Vision Engine
======================================================================
 Model: yolov8s.pt
 Video: videos/city_traffic.mp4
 Target FPS: 15
 Streets monitored: 1
 Parking spots: 2
======================================================================

✓ Using GPU: NVIDIA GeForce RTX 4060
✓ Connected to Redis at localhost:6379
Video info: 1920x1080 @ 30.0 FPS, 5400 frames
Processing started... Press 'q' to quit
```

---

## 📁 Project Structure

```
UrbanFlow/
├── detector.py           # Main vision engine (run this 24/7)
├── roi_editor.py         # Interactive ROI definition tool
├── config.yaml           # Configuration (ROIs, thresholds, Redis)
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── videos/
│   └── city_traffic.mp4  # Your video file
└── venv/                # Virtual environment
```

---

## ⚙️ Configuration Guide

### `config.yaml` - Full Reference

```yaml
# ============================================
# VIDEO SOURCE
# ============================================
video:
  source: "videos/city_traffic.mp4"
  display_preview: true      # Show live detection window
  target_fps: 15             # Processing speed (10-15 recommended)

# ============================================
# YOLO MODEL
# ============================================
model:
  weights: "yolov8s.pt"      # YOLOv8 small (good speed/accuracy balance)
  confidence: 0.5            # Detection threshold
  device: "cuda"             # "cuda" for GPU, "cpu" for CPU
  classes_to_detect:
    - 2  # car
    - 3  # motorcycle
    - 5  # bus
    - 7  # truck (emergency vehicle stand-in)

# ============================================
# REDIS CONNECTION
# ============================================
redis:
  host: "localhost"
  port: 6379
  db: 0
  # password: "your_password"  # Uncomment if needed

# ============================================
# TRAFFIC MONITORING
# ============================================
traffic:
  streets:
    street_1:
      roi: [[100,200], [500,200], [500,600], [100,600]]  # Polygon points
      max_vehicles: 20          # Max cars before 100% congestion
      redis_key: "urbanflow:traffic:street_1"

# ============================================
# PARKING MONITORING
# ============================================
parking:
  spots:
    SPOT_A1:
      roi: [[50,50], [150,50], [150,150], [50,150]]
      redis_key: "urbanflow:parking:SPOT_A1"

# ============================================
# EMERGENCY VEHICLE TRACKING
# ============================================
emergency:
  vehicle_class: 7           # COCO class 7 = truck
  track_all: true
  redis_key_prefix: "urbanflow:emergency:truck_"
```

---

## 🔧 How It Works

### Detection Pipeline

```
Video Frame → YOLOv8 → Bounding Boxes → ROI Analysis → Redis Publish
     ↓           ↓           ↓              ↓             ↓
   1080p    GPU Inference  [x,y,w,h]   Point-in-Polygon  Backend
```

### 1. **Traffic Density** (Street ROIs)

```python
# For each street ROI:
vehicles_in_roi = count_vehicles_in_polygon(detections, street_roi)
density = min(vehicles_in_roi / max_vehicles, 1.0)

# Publish
redis.set("urbanflow:traffic:street_1", density)  # 0.0 to 1.0
```

### 2. **Parking Status** (Spot ROIs)

```python
# For each parking spot:
car_detected = any_car_center_in_polygon(detections, spot_roi)
status = "occupied" if car_detected else "free"

# Publish
redis.set("urbanflow:parking:SPOT_A1", status)
```

### 3. **Emergency Tracking** (Truck Detection)

```python
# For each truck (COCO class 7):
truck_center = get_bbox_center(truck_bbox)
payload = {
    "id": "truck_01",
    "location": [x, y],
    "bbox": [x1, y1, x2, y2],
    "timestamp": 1234567890
}

# Publish
redis.set("urbanflow:emergency:truck_01", json.dumps(payload))
```

---

## 🐛 Troubleshooting

### Issue: "CUDA not available"
**Solution:** You're on CPU mode. It will work but slower (~5 FPS instead of 15 FPS)
```bash
# Check PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

### Issue: "Could not connect to Redis"
**Solution:** Install and start Redis
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

### Issue: "Video file not found"
**Solution:** Update `config.yaml` with correct path
```yaml
video:
  source: "videos/city_traffic.mp4"  # Check this path
```

### Issue: Low FPS / Slow Processing
**Solutions:**
1. Lower `target_fps` in config (try 10 instead of 15)
2. Use smaller model: `yolov8n.pt` instead of `yolov8s.pt`
3. Reduce video resolution (use 720p instead of 1080p)
4. Lower confidence threshold: `confidence: 0.4`

---

## 📊 Redis Data Schema

### Traffic Keys
```
Key: urbanflow:traffic:street_1
Type: String
Value: "0.82" (float as string, 0.0-1.0)
TTL: No expiry
```

### Parking Keys
```
Key: urbanflow:parking:SPOT_A1
Type: String
Value: "occupied" or "free"
TTL: No expiry
```

### Emergency Keys
```
Key: urbanflow:emergency:truck_01
Type: String
Value: '{"id": "truck_01", "location": [450, 320], "bbox": [...], "timestamp": 1234567890}'
TTL: 5 seconds (auto-expires if vehicle not detected)
```

---

## 🎓 Technical Details

### COCO Classes Used
| Class ID | Object | Usage |
|----------|--------|-------|
| 2 | Car | Traffic + Parking |
| 3 | Motorcycle | Traffic only |
| 5 | Bus | Traffic only |
| 7 | Truck | Emergency vehicle (stand-in for ambulance) |

### Performance Specs
- **Hardware:** NVIDIA RTX 4060 (recommended), CPU also works
- **Model:** YOLOv8s (~11M parameters)
- **Target FPS:** 10-15 FPS
- **Resolution:** 1080p or 720p
- **Latency:** <100ms per frame

### Algorithm: Point-in-Polygon
Uses ray casting algorithm to determine if vehicle center is inside ROI:
- Cast horizontal ray from point to infinity
- Count polygon edge intersections
- Odd count = inside, Even count = outside

---

## 🔮 Future Enhancements

- [ ] Multi-camera support (multiple video feeds)
- [ ] Object tracking (DeepSORT) for persistent vehicle IDs
- [ ] Traffic flow vectors (direction + speed estimation)
- [ ] Real RTSP stream support (live cameras)
- [ ] GPU batch processing for multiple streams
- [ ] Web dashboard for live visualization

---

## 🤝 Backend Integration

**For Backend Engineers:**

Your detector is running. To consume the data:

```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Get traffic density
street_1_density = float(r.get("urbanflow:traffic:street_1") or 0)

# Get parking status
spot_a1_status = r.get("urbanflow:parking:SPOT_A1")  # "occupied" or "free"

# Get emergency vehicles
emergency_keys = r.keys("urbanflow:emergency:truck_*")
for key in emergency_keys:
    data = json.loads(r.get(key))
    print(f"Emergency vehicle at {data['location']}")
```

---

## 📝 License

UrbanFlowAI - Intelligent Urban Mobility Orchestration Platform

---

## 💡 Support

For questions or issues:
1. Check `config.yaml` settings
2. Verify video path and ROI definitions
3. Test Redis connection: `redis-cli ping`
4. Check GPU availability if using CUDA

**Built with:** Python 3.8+, YOLOv8, OpenCV, Redis

**The Foundation of UrbanFlowAI** - Without these "Eyes," the "Brain" is blind. 🚀

