# 📡 UrbanFlowAI API Documentation

**For Role 3 (Frontend Engineers)**

This document provides complete API reference for integrating with UrbanFlowAI backend.

---

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

---

## Authentication

Currently no authentication required for development.

**For Production**: Add API key header:
```
X-API-Key: your-api-key
```

---

## Endpoints Overview

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check system health |
| `/api/v1/status/live` | GET | Get real-time city status |
| `/api/v1/route/calculate` | POST | Calculate route |

---

## 1. Health Check

### `GET /health`

Check if the API and its dependencies are running.

**Request:**
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "redis": "connected",
    "database": "connected"
  }
}
```

**Status Codes:**
- `200 OK`: System is healthy
- `503 Service Unavailable`: System is degraded

**Usage:**
```javascript
const response = await fetch('http://localhost:8000/health');
const health = await response.json();

if (health.status !== 'healthy') {
  console.warn('System degraded:', health.services);
}
```

---

## 2. Live Status (Primary Dashboard Endpoint)

### `GET /api/v1/status/live`

Get a real-time snapshot of the entire city.

**Update Frequency**: Call every 5-10 seconds for live dashboard.

**Request:**
```http
GET /api/v1/status/live HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "streets": [
    {
      "street_id": "street_1",
      "street_name": "Main Street",
      "congestion_score": 0.75,
      "congestion_level": "high",
      "coordinates": [
        [-73.9857, 40.7484],
        [-73.9847, 40.7494]
      ]
    }
  ],
  "average_congestion": 0.45,
  "parking_zones": [
    {
      "zone_id": "zone_A",
      "zone_name": "Central Parking",
      "total_spots": 50,
      "free_spots": 23,
      "occupancy_rate": 0.54,
      "latitude": 40.7489,
      "longitude": -73.9852
    }
  ],
  "total_parking_spots": 80,
  "total_free_spots": 35,
  "emergency_vehicles": [
    {
      "vehicle_id": "amb_001",
      "vehicle_type": "ambulance",
      "latitude": 40.7489,
      "longitude": -73.9852,
      "heading": 45.0,
      "speed": 60.0,
      "status": "responding",
      "last_updated": "2024-01-15T10:30:00.000Z"
    }
  ],
  "active_emergencies": 1
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO 8601 | When this snapshot was generated |
| `streets` | Array | List of all street segments with traffic data |
| `streets[].street_id` | String | Unique street identifier |
| `streets[].street_name` | String | Human-readable street name |
| `streets[].congestion_score` | Float | Traffic density (0.0 = free, 1.0 = gridlock) |
| `streets[].congestion_level` | Enum | `low`, `medium`, `high`, `critical` |
| `streets[].coordinates` | Array | [[lon, lat], ...] for map display |
| `average_congestion` | Float | City-wide average congestion |
| `parking_zones` | Array | Parking zone summaries |
| `parking_zones[].zone_id` | String | Zone identifier |
| `parking_zones[].zone_name` | String | Zone name |
| `parking_zones[].total_spots` | Integer | Total parking capacity |
| `parking_zones[].free_spots` | Integer | Currently available spots |
| `parking_zones[].occupancy_rate` | Float | 0.0 to 1.0 (1.0 = full) |
| `total_parking_spots` | Integer | City-wide total spots |
| `total_free_spots` | Integer | City-wide free spots |
| `emergency_vehicles` | Array | Active emergency vehicles |
| `active_emergencies` | Integer | Count of responding vehicles |

**JavaScript Example:**

```javascript
// Fetch live status every 10 seconds
async function updateDashboard() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/status/live');
    const data = await response.json();
    
    // Update traffic map
    updateTrafficMap(data.streets);
    
    // Update parking display
    updateParkingWidget(data.parking_zones);
    
    // Update emergency alerts
    updateEmergencyAlerts(data.emergency_vehicles);
    
    // Update statistics
    document.getElementById('avg-congestion').textContent = 
      `${(data.average_congestion * 100).toFixed(0)}%`;
    document.getElementById('free-parking').textContent = 
      `${data.total_free_spots}/${data.total_parking_spots}`;
    
  } catch (error) {
    console.error('Failed to fetch live status:', error);
  }
}

// Start live updates
setInterval(updateDashboard, 10000);
updateDashboard(); // Initial call
```

**React Example:**

```jsx
import { useState, useEffect } from 'react';

function LiveDashboard() {
  const [liveData, setLiveData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLiveStatus = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/v1/status/live');
        const data = await res.json();
        setLiveData(data);
        setLoading(false);
      } catch (err) {
        console.error(err);
      }
    };

    fetchLiveStatus();
    const interval = setInterval(fetchLiveStatus, 10000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>City Dashboard</h1>
      <div>Average Congestion: {(liveData.average_congestion * 100).toFixed(0)}%</div>
      <div>Free Parking: {liveData.total_free_spots}</div>
      <div>Active Emergencies: {liveData.active_emergencies}</div>
      
      {/* Display streets on map */}
      {liveData.streets.map(street => (
        <StreetSegment key={street.street_id} data={street} />
      ))}
    </div>
  );
}
```

---

## 3. Route Calculation

### `POST /api/v1/route/calculate`

Calculate intelligent routes based on selected mode.

**Modes:**
- **citizen**: Standard fast routing for regular users
- **emergency**: Priority routing that avoids congested streets
- **smartpark**: Navigate to nearest free parking

**Request:**
```http
POST /api/v1/route/calculate HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "start": {
    "latitude": 40.7489,
    "longitude": -73.9852
  },
  "end": {
    "latitude": 40.7599,
    "longitude": -73.9762
  },
  "mode": "citizen",
  "vehicle_id": null
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `start` | Object | Yes | Starting GPS coordinate |
| `start.latitude` | Float | Yes | -90 to 90 |
| `start.longitude` | Float | Yes | -180 to 180 |
| `end` | Object | Yes | Destination GPS coordinate |
| `end.latitude` | Float | Yes | -90 to 90 |
| `end.longitude` | Float | Yes | -180 to 180 |
| `mode` | Enum | Yes | `citizen`, `emergency`, or `smartpark` |
| `vehicle_id` | String | Conditional | Required for `emergency` mode |

**Response:**
```json
{
  "mode": "emergency",
  "start": {
    "latitude": 40.7489,
    "longitude": -73.9852
  },
  "end": {
    "latitude": 40.7599,
    "longitude": -73.9762
  },
  "coordinates": [
    [-73.9852, 40.7489],
    [-73.9850, 40.7495],
    [-73.9762, 40.7599]
  ],
  "total_distance": 1250.5,
  "total_duration": 180.0,
  "steps": [
    {
      "instruction": "Head north on Main St",
      "distance": 500.0,
      "duration": 60.0,
      "coordinates": [[-73.9852, 40.7489], [-73.9850, 40.7495]]
    },
    {
      "instruction": "Turn right onto Broadway",
      "distance": 750.5,
      "duration": 120.0,
      "coordinates": [[-73.9850, 40.7495], [-73.9762, 40.7599]]
    }
  ],
  "calculated_at": "2024-01-15T10:30:00.000Z",
  "avoided_congested_streets": ["street_2", "street_5"],
  "destination_parking_zone": null,
  "available_spots_at_destination": null
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `mode` | String | The routing mode used |
| `coordinates` | Array | [[lon, lat], ...] Full route path |
| `total_distance` | Float | Total distance in meters |
| `total_duration` | Float | Estimated time in seconds |
| `steps` | Array | Turn-by-turn navigation steps |
| `steps[].instruction` | String | Human-readable direction |
| `steps[].distance` | Float | Step distance in meters |
| `steps[].duration` | Float | Step duration in seconds |
| `avoided_congested_streets` | Array | (Emergency only) Streets avoided |
| `destination_parking_zone` | String | (SmartPark only) Recommended zone |
| `available_spots_at_destination` | Integer | (SmartPark only) Free spots count |

**JavaScript Example - Citizen Mode:**

```javascript
async function calculateRoute(start, end) {
  const response = await fetch('http://localhost:8000/api/v1/route/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      start: { latitude: start.lat, longitude: start.lng },
      end: { latitude: end.lat, longitude: end.lng },
      mode: 'citizen'
    })
  });
  
  const route = await response.json();
  
  // Display route on map (e.g., Leaflet, Mapbox)
  displayRouteOnMap(route.coordinates);
  
  // Show navigation
  displaySteps(route.steps);
  
  // Show ETA
  const minutes = Math.round(route.total_duration / 60);
  const km = (route.total_distance / 1000).toFixed(1);
  console.log(`Route: ${km} km, ${minutes} minutes`);
  
  return route;
}
```

**JavaScript Example - Emergency Mode:**

```javascript
async function getEmergencyRoute(ambulanceId, start, destination) {
  const response = await fetch('http://localhost:8000/api/v1/route/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      start: { latitude: start.lat, longitude: start.lng },
      end: { latitude: destination.lat, longitude: destination.lng },
      mode: 'emergency',
      vehicle_id: ambulanceId
    })
  });
  
  const route = await response.json();
  
  // Highlight avoided streets
  if (route.avoided_congested_streets) {
    highlightAvoidedStreets(route.avoided_congested_streets);
  }
  
  // Display priority route
  displayPriorityRoute(route.coordinates);
  
  return route;
}
```

**JavaScript Example - SmartPark Mode:**

```javascript
async function findParking(currentLocation) {
  const response = await fetch('http://localhost:8000/api/v1/route/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      start: { 
        latitude: currentLocation.lat, 
        longitude: currentLocation.lng 
      },
      end: { 
        latitude: currentLocation.lat,  // Will be replaced by nearest parking
        longitude: currentLocation.lng 
      },
      mode: 'smartpark'
    })
  });
  
  const route = await response.json();
  
  // Show parking info
  console.log(`Parking Zone: ${route.destination_parking_zone}`);
  console.log(`Available Spots: ${route.available_spots_at_destination}`);
  
  // Navigate to parking
  displayRouteOnMap(route.coordinates);
  
  return route;
}
```

**Error Responses:**

```json
// 400 Bad Request - Invalid input
{
  "detail": "vehicle_id is required for emergency mode"
}

// 500 Internal Server Error
{
  "detail": "Failed to calculate route: OSRM service unavailable"
}
```

---

## Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input parameters |
| 422 | Validation Error | Request body doesn't match schema |
| 500 | Server Error | Internal error (check logs) |
| 503 | Service Unavailable | Routing engine down |

---

## Complete Integration Example

```javascript
class UrbanFlowAPI {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async checkHealth() {
    const res = await fetch(`${this.baseUrl}/health`);
    return res.json();
  }

  async getLiveStatus() {
    const res = await fetch(`${this.baseUrl}/api/v1/status/live`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

  async calculateRoute(start, end, mode, vehicleId = null) {
    const res = await fetch(`${this.baseUrl}/api/v1/route/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        start: { latitude: start.lat, longitude: start.lng },
        end: { latitude: end.lat, longitude: end.lng },
        mode,
        vehicle_id: vehicleId
      })
    });
    
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Route calculation failed');
    }
    
    return res.json();
  }
}

// Usage
const api = new UrbanFlowAPI();

// Check health
const health = await api.checkHealth();
console.log('API Status:', health.status);

// Get live data
const liveData = await api.getLiveStatus();
console.log('Free parking spots:', liveData.total_free_spots);

// Calculate route
const route = await api.calculateRoute(
  { lat: 40.7489, lng: -73.9852 },
  { lat: 40.7599, lng: -73.9762 },
  'citizen'
);
console.log('Route distance:', route.total_distance, 'meters');
```

---

## WebSocket Support (Future)

Currently not implemented. Use HTTP polling (every 10 seconds) for live updates.

**Planned for v2.0:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/live');
ws.onmessage = (event) => {
  const liveData = JSON.parse(event.data);
  updateDashboard(liveData);
};
```

---

## Rate Limiting

**Current**: No rate limiting

**Production Recommendations**:
- Live Status: Max 1 request per 5 seconds per client
- Route Calculation: Max 10 requests per minute per client

---

## CORS

CORS is enabled for all origins in development.

**Production**: Configure specific origins in backend.

---

## Support

- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

---

## Changelog

**v1.0.0** (Initial Release)
- Live Status endpoint
- Route Calculation (3 modes)
- Health check endpoint

---

**Built for Role 3 (Frontend) by Role 2 (Backend)** 🤝

