# UrbanFlowAI - Multi-Video Setup Guide

> **Run multiple camera feeds simultaneously!**

---

## 📹 **Current Setup:**

### **Video 1: Traffic (Intersection)**
- **File:** `video.mp4` (4K traffic intersection)
- **Config:** `config.yaml`
- **Focus:** Traffic density + some parking
- **Streets:** 4 ROIs monitored
- **Parking:** 2 spots

### **Video 2: Parking Lot (NEW)**  
- **File:** `parking.mp4` (your new parking lot video)
- **Config:** `config_parking.yaml`
- **Focus:** Parking occupancy
- **Streets:** None
- **Parking:** 10+ spots (expandable to 50+)

---

## 🚀 **Quick Start:**

### **Step 1: Add Your Parking Video**
```bash
# Place your parking lot video in the project folder
# Name it: parking.mp4
```

### **Step 2: Define Parking ROIs**
```bash
# Run ROI editor for parking lot video
python roi_editor.py --config config_parking.yaml
```

**Instructions:**
- The parking lot video will load
- Press **'t'** to switch to PARKING mode (magenta)
- Draw rectangles around each parking spot
- Press **'c'** after each spot
- Press **'s'** to save all ROIs
- Press **'q'** to quit

---

## 🎬 **Running Detectors:**

### **Option 1: Run Traffic Only**
```bash
./run_traffic.sh
# OR
python detector.py --config config.yaml
```

### **Option 2: Run Parking Only**
```bash
./run_parking.sh
# OR
python detector.py --config config_parking.yaml
```

### **Option 3: Run Both in Parallel** ⭐
```bash
./run_both.sh
```

**This will:**
- Start traffic detector (window 1)
- Start parking detector (window 2)
- Both publish to Redis simultaneously
- Press Ctrl+C to stop both

---

## 📊 **Redis Data Output:**

### **Traffic Video:**
```
urbanflow:traffic:street_1 → "0.82"  # 82% density
urbanflow:traffic:street_2 → "0.45"
urbanflow:parking:SPOT_A1 → "occupied"
urbanflow:parking:SPOT_A2 → "free"
```

### **Parking Video:**
```
urbanflow:parking:SPOT_P1 → "occupied"
urbanflow:parking:SPOT_P2 → "free"
urbanflow:parking:SPOT_P3 → "occupied"
...
urbanflow:parking:SPOT_P10 → "free"
```

**All data goes to the same Redis instance!** Backend reads from one place.

---

## ⚙️ **Configuration:**

### **Add More Parking Spots:**

Edit `config_parking.yaml`:

```yaml
parking:
  spots:
    SPOT_P11:
      roi: []
      redis_key: "urbanflow:parking:SPOT_P11"
    
    SPOT_P12:
      roi: []
      redis_key: "urbanflow:parking:SPOT_P12"
    
    # Add as many as you need!
```

Then run ROI editor again to define the new spots.

---

## 🔧 **System Requirements:**

**For 2 Videos Running Simultaneously:**
- GPU: RTX 4060 (you have this ✅)
- RAM: 8GB+ recommended
- Both will share the GPU
- Expected FPS: ~10-15 per detector

**Performance:**
- Traffic: ~15 FPS (4K video, complex scene)
- Parking: ~20+ FPS (usually simpler, fewer objects)

---

## 💡 **Tips:**

### **Parking Spot Naming Convention:**
```
Row A: SPOT_P1, SPOT_P2, SPOT_P3...
Row B: SPOT_P11, SPOT_P12, SPOT_P13...
Row C: SPOT_P21, SPOT_P22, SPOT_P23...
```

### **Drawing Parking ROIs:**
1. **Be generous** - make boxes slightly larger than the car
2. **Consistent spacing** - helps avoid overlaps
3. **Label visible** - center of ROI for labels

### **Testing Individual Cameras:**
```bash
# Test traffic first
python detector.py --config config.yaml

# Test parking separately
python detector.py --config config_parking.yaml

# Then run both together
./run_both.sh
```

---

## 🐛 **Troubleshooting:**

### **"GPU Out of Memory"**
If running both crashes:
1. Lower `target_fps` in both configs to 10
2. Or run them one at a time
3. Or reduce `imgsz` back to 640 in detector.py

### **Wrong Video Loading**
Check the `source` path in each config file:
- `config.yaml` → `source: "video.mp4"` (traffic)
- `config_parking.yaml` → `source: "parking.mp4"` (parking)

### **ROIs Not Saving**
Make sure you're using the right config:
```bash
# For parking lot ROIs:
python roi_editor.py --config config_parking.yaml
```

---

## 📈 **Scalability:**

**Want to add more cameras?**

1. Create `config_camera3.yaml`
2. Set different `source:` video
3. Use unique `redis_key:` prefixes
4. Run: `python detector.py --config config_camera3.yaml`

**You can run 3-4 cameras on your RTX 4060!**

---

## 🎯 **Next Steps:**

1. ✅ Get your parking lot video (`parking.mp4`)
2. ✅ Run ROI editor: `python roi_editor.py --config config_parking.yaml`
3. ✅ Draw 10-20 parking spot ROIs
4. ✅ Test: `./run_parking.sh`
5. ✅ Run both: `./run_both.sh`
6. ✅ Backend integration (Redis already configured!)

---

**Your UrbanFlowAI Vision Engine is now a multi-camera system!** 🎥🚀

