# 🚦 UrbanFlowAI

**AI-powered traffic and parking management system using computer vision**

[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![YOLO](https://img.shields.io/badge/YOLO-v11-green)](https://github.com/ultralytics/ultralytics)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)

---

## 🎯 What It Does

UrbanFlowAI monitors urban traffic and parking in real-time using AI vision:

- 🚗 **Traffic Monitoring** - Detects vehicles and calculates congestion scores
- 🅿️ **Parking Detection** - Tracks parking spot occupancy
- ⚡ **Speed Tracking** - Measures vehicle speeds
- 📊 **Real-time Analytics** - Metrics and statistics
- 🗺️ **REST API** - Ready for frontend integration

---

## 🚀 Quick Start

### 1. Start Backend

```bash
cd Heaven
docker-compose up -d
```

### 2. Install Vision Engine

```bash
cd VisionEngine
pip install -r requirements.txt
```

### 3. Run Detection

```bash
# Traffic monitoring
python scripts/detector.py

# Parking monitoring
python scripts/parking_detector.py --config config/config_parking.yaml
```

### 4. Access API

```
http://localhost:8000/docs
```

---

## 📁 Project Structure

```
UrbanFlow/
├── Heaven/                 # Backend API (FastAPI + Docker)
│   ├── api/                # REST API endpoints
│   ├── docker-compose.yml  # Infrastructure setup
│   └── init-db/            # Database initialization
│
├── VisionEngine/           # AI Vision Processing
│   ├── scripts/            # Python detection scripts
│   │   ├── detector.py         # Traffic monitoring
│   │   ├── parking_detector.py # Parking detection
│   │   ├── roi_editor.py       # ROI configuration
│   │   └── calibrate_speed.py  # Speed calibration
│   ├── config/             # Configuration files
│   │   ├── config.yaml          # Traffic config
│   │   └── config_parking.yaml  # Parking config
│   ├── metrics/            # Real-time metrics output
│   └── requirements.txt    # Python dependencies
│
└── docs/                   # Documentation
    ├── SETUP_GUIDE.md      # Installation & configuration
    ├── USER_GUIDE.md       # Features & usage
    └── FOR_DEVELOPERS.md   # API & frontend development
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Vision** | YOLOv11, OpenCV, Python |
| **Backend** | FastAPI, Redis, PostgreSQL |
| **Routing** | OSRM, GraphHopper |
| **Infrastructure** | Docker, Docker Compose |
| **Frontend** | *To be built* |

---

## 📊 Features

### Traffic Monitoring
- ✅ Real-time vehicle detection
- ✅ Congestion scoring (0-100%)
- ✅ Speed measurement
- ✅ Multi-street support
- ✅ Emergency vehicle detection

### Parking Detection
- ✅ Spot occupancy tracking
- ✅ Adaptive detection (overhead views)
- ✅ Manual ROI drawing
- ✅ Auto-learning parking spots
- ✅ Grid generation

### Analytics
- ✅ Real-time metrics (JSON)
- ✅ Historical data (CSV)
- ✅ Per-street statistics
- ✅ Parking occupancy rates

### API
- ✅ RESTful endpoints
- ✅ Live city status
- ✅ Route calculation
- ✅ Interactive documentation

---

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| [**SETUP_GUIDE.md**](docs/SETUP_GUIDE.md) | Installation, configuration, troubleshooting |
| [**USER_GUIDE.md**](docs/USER_GUIDE.md) | Features, usage, best practices |
| [**FOR_DEVELOPERS.md**](docs/FOR_DEVELOPERS.md) | API docs, frontend development |

---

## 🔌 API Example

### Get Live Status

```bash
curl http://localhost:8000/api/v1/status/live
```

**Response:**

```json
{
  "timestamp": "2025-10-23T15:30:00",
  "streets": [
    {
      "street_id": "street_1",
      "congestion_score": 0.21,
      "congestion_level": "low"
    }
  ],
  "parking_zones": [
    {
      "zone_id": "zone_A",
      "total_spots": 10,
      "free_spots": 4,
      "occupancy_rate": 0.6
    }
  ]
}
```

**More examples:** See [FOR_DEVELOPERS.md](docs/FOR_DEVELOPERS.md)

---

## 🎨 Screenshots

### Traffic Detection
```
🚗 Detecting vehicles...
Street 1: ████░░░░░░ 21% (Low)
Street 2: █████░░░░░ 55% (Medium)
Street 3: ████████░░ 80% (High)
Street 4: ███░░░░░░░ 30% (Low)
```

### Parking Occupancy
```
🅿️  Parking Status:
Zone A: [■■■■■■□□□□] 60% Full (6/10)
Zone B: [■■■■■■■■□□] 80% Full (8/10)
```

---

## ⚡ Performance

| Metric | Value |
|--------|-------|
| **Detection FPS** | 15 FPS |
| **API Latency** | < 50ms |
| **Update Frequency** | 2 seconds |
| **Accuracy** | > 90% (vehicles) |
| **Speed Accuracy** | ±5 km/h |

---

## 🌟 Use Cases

- **Smart Cities** - Real-time traffic management
- **Parking Management** - Optimize parking utilization
- **Emergency Services** - Priority routing
- **Urban Planning** - Traffic pattern analysis
- **Research** - Transportation studies

---

## 🛣️ Roadmap

### MVP (Current)
- [x] Vehicle detection
- [x] Traffic monitoring
- [x] Parking detection
- [x] Speed tracking
- [x] REST API
- [ ] Frontend UI *(in progress)*

### Future
- [ ] Multi-camera support
- [ ] Historical analytics dashboard
- [ ] Traffic prediction (ML)
- [ ] Mobile app
- [ ] Cloud deployment
- [ ] Emergency vehicle prioritization

---

## 🤝 Contributing

We welcome contributions! Please see our [contribution guidelines](docs/FOR_DEVELOPERS.md#contributing).

### Development Setup

```bash
# Clone repository
git clone https://github.com/Stupu-Eduard/UrbanFlow.git
cd UrbanFlow

# Setup backend
cd Heaven && docker-compose up -d

# Setup vision engine
cd ../VisionEngine
pip install -r requirements.txt

# Start developing!
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**HeavenSolutions** - Hackathon Project

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **API Docs**: http://localhost:8000/docs
- **Issues**: [GitHub Issues](https://github.com/Stupu-Eduard/UrbanFlow/issues)

---

## 🎉 Acknowledgments

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) - Object detection
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [OpenCV](https://opencv.org/) - Computer vision
- [Redis](https://redis.io/) - Real-time data
- [PostgreSQL](https://www.postgresql.org/) - Database

---

**Made with ❤️ for smarter cities**

*For detailed setup instructions, see [SETUP_GUIDE.md](docs/SETUP_GUIDE.md)*
