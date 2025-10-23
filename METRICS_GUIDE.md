# 📊 UrbanFlowAI - Metrics & Reporting

Real-time metrics collection and historical logging for traffic and parking analysis.

---

## 📁 Output Files

All metrics are saved to the `metrics/` directory:

### 1. **`current_metrics.json`** (Real-time Snapshot)
Updated every frame. Contains the latest traffic and parking statistics.

```json
{
  "timestamp": "2025-10-23T14:27:45.058662",
  "last_updated": "2025-10-23 14:27:45",
  "parking": {
    "total_spots": 26,
    "occupied_spots": 18,
    "available_spots": 8,
    "occupancy_percentage": 69.2
  },
  "traffic": {
    "total_vehicles": 53,
    "average_density_percentage": 50.7,
    "average_speed_kmh": 12.7,
    "speeding_vehicles": 0,
    "streets": {
      "street_1": {
        "vehicle_count": 16,
        "density": 0.178,
        "avg_speed": 25.0,
        "speeding_count": 0
      }
    }
  }
}
```

**Use case:** Backend dashboard, real-time monitoring, APIs

---

### 2. **`metrics_history.csv`** (Time-series Data)
Appended every **5 seconds**. Perfect for analysis and charting.

```csv
timestamp,parking_total,parking_occupied,parking_available,parking_occupancy_pct,traffic_total_vehicles,traffic_avg_density_pct,traffic_avg_speed_kmh,speeding_vehicles
2025-10-23T14:27:29.532007,26,18,8,69.2,48,44.4,12.5,0
2025-10-23T14:27:34.612891,26,20,6,76.9,52,48.3,11.8,1
```

**Use case:** Historical analysis, graphs, reports, machine learning

---

## 🎯 Key Metrics Explained

### Parking Metrics
- **`total_spots`**: Total parking spots defined in ROIs
- **`occupied_spots`**: Number of spots with cars detected
- **`available_spots`**: `total_spots - occupied_spots`
- **`occupancy_percentage`**: `(occupied / total) × 100`

### Traffic Metrics
- **`total_vehicles`**: Total vehicles detected across all streets
- **`average_density_percentage`**: Average congestion across all streets
  - Formula: `(vehicle_count / max_vehicles) × 100`
  - 0% = empty, 100% = maximum capacity
- **`average_speed_kmh`**: Average speed of tracked vehicles (km/h)
- **`speeding_vehicles`**: Number of vehicles exceeding speed limit

### Per-Street Metrics
- **`vehicle_count`**: Vehicles in this street ROI
- **`density`**: Congestion ratio (0.0 to 1.0)
- **`avg_speed`**: Average speed in this street
- **`speeding_count`**: Speeding vehicles in this street

---

## 🚀 How It Works

### 1. **Traffic Script** (`detector.py`)
```bash
python detector.py
# Metrics automatically logged to metrics/
```

### 2. **Parking Script** (`parking_detector.py`)
```bash
python parking_detector.py
# Metrics automatically logged to metrics/
```

### 3. **Integration Automatic**
- **Real-time**: `current_metrics.json` updates every frame
- **History**: `metrics_history.csv` appends every 5 seconds
- **No configuration needed**: Works out of the box!

---

## 📈 Using the Data

### Python Example
```python
import json
import pandas as pd

# Read current snapshot
with open('metrics/current_metrics.json', 'r') as f:
    data = json.load(f)
    
print(f"Parking occupancy: {data['parking']['occupancy_percentage']}%")
print(f"Traffic density: {data['traffic']['average_density_percentage']}%")

# Read historical data
df = pd.read_csv('metrics/metrics_history.csv')
print(df.describe())
```

### Backend API Integration
```javascript
// Node.js example
const metrics = require('./metrics/current_metrics.json');

app.get('/api/parking/status', (req, res) => {
  res.json({
    total: metrics.parking.total_spots,
    occupied: metrics.parking.occupied_spots,
    available: metrics.parking.available_spots,
    occupancy: metrics.parking.occupancy_percentage
  });
});
```

---

## 🔧 Configuration

Metrics logging interval is **5 seconds** by default.

To change it, edit `metrics_logger.py`:
```python
self.log_interval = 5  # Change to desired seconds
```

---

## 📊 Visualization Ideas

1. **Real-time Dashboard**
   - Read `current_metrics.json` every second
   - Display occupancy bars, density gauges

2. **Historical Charts**
   - Import `metrics_history.csv` into Excel/Google Sheets
   - Create line graphs for occupancy/density over time

3. **Traffic Analysis**
   - Compare peak hours
   - Identify congestion patterns
   - Speed violation reports

4. **Parking Analytics**
   - Average occupancy per hour
   - Turnover rate
   - Utilization efficiency

---

## 🎯 Next Steps

1. ✅ Metrics are automatically collected
2. ✅ Files are updated in real-time
3. 🚀 Build your dashboard using the JSON/CSV outputs
4. 📊 Analyze trends with your favorite tools

**No changes to your detector scripts needed!**

---

## 📁 File Structure
```
UrbanFlow/
├── detector.py              # Traffic monitoring (auto-logs metrics)
├── parking_detector.py      # Parking monitoring (auto-logs metrics)
├── metrics_logger.py        # Metrics engine (automatic)
└── metrics/
    ├── current_metrics.json # Latest snapshot
    └── metrics_history.csv  # Time-series data
```

---

**Questions?** Check the implementation in `metrics_logger.py` for details.

