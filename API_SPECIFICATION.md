# 🎨 UrbanFlowAI - API Specification for UI Development

**Base URL:** `http://localhost:8000`

---

## 🚀 Main Endpoint (Use This!)

### GET `/api/v1/status/live`

**Returns:** Complete real-time city status

**Response:**

```json
{
  "timestamp": "2025-10-23T15:30:00.000Z",
  "streets": [
    {
      "street_id": "street_1",
      "street_name": "Main Intersection - North",
      "congestion_score": 0.21,
      "congestion_level": "low",
      "coordinates": [[-73.98, 40.75], [-73.97, 40.76]],
      "max_speed": 50
    },
    {
      "street_id": "street_2",
      "street_name": "Main Intersection - South",
      "congestion_score": 0.55,
      "congestion_level": "medium",
      "coordinates": [[-147.96, 40.75], [-147.94, 40.76]],
      "max_speed": 50
    },
    {
      "street_id": "street_3",
      "street_name": "Main Intersection - East",
      "congestion_score": 0.80,
      "congestion_level": "high",
      "coordinates": [[-221.94, 40.75], [-221.91, 40.76]],
      "max_speed": 70
    },
    {
      "street_id": "street_4",
      "street_name": "Main Intersection - West",
      "congestion_score": 0.30,
      "congestion_level": "low",
      "coordinates": [[-295.92, 40.75], [-295.88, 40.76]],
      "max_speed": 40
    }
  ],
  "average_congestion": 0.44,
  "parking_zones": [
    {
      "zone_id": "zone_A",
      "zone_name": "Central Parking Lot",
      "total_spots": 10,
      "free_spots": 4,
      "occupancy_rate": 0.6,
      "latitude": 40.7589,
      "longitude": -73.9762,
      "spots": [
        {"spot_id": "SPOT_A1", "status": "occupied"},
        {"spot_id": "SPOT_A2", "status": "free"},
        {"spot_id": "SPOT_A3", "status": "occupied"},
        {"spot_id": "SPOT_A4", "status": "occupied"},
        {"spot_id": "SPOT_A5", "status": "free"},
        {"spot_id": "SPOT_A6", "status": "occupied"},
        {"spot_id": "SPOT_A7", "status": "occupied"},
        {"spot_id": "SPOT_A8", "status": "free"},
        {"spot_id": "SPOT_A9", "status": "occupied"},
        {"spot_id": "SPOT_A10", "status": "free"}
      ]
    },
    {
      "zone_id": "zone_B",
      "zone_name": "North Parking Area",
      "total_spots": 8,
      "free_spots": 3,
      "occupancy_rate": 0.625,
      "latitude": 40.7609,
      "longitude": -73.9762,
      "spots": [
        {"spot_id": "SPOT_B1", "status": "occupied"},
        {"spot_id": "SPOT_B2", "status": "occupied"},
        {"spot_id": "SPOT_B3", "status": "free"},
        {"spot_id": "SPOT_B4", "status": "occupied"},
        {"spot_id": "SPOT_B5", "status": "free"},
        {"spot_id": "SPOT_B6", "status": "occupied"},
        {"spot_id": "SPOT_B7", "status": "occupied"},
        {"spot_id": "SPOT_B8", "status": "free"}
      ]
    }
  ],
  "total_parking_spots": 18,
  "total_free_spots": 7,
  "emergency_vehicles": [],
  "active_emergencies": 0
}
```

---

## 📊 Data Models (TypeScript)

```typescript
// Main Response
interface LiveStatus {
  timestamp: string;
  streets: Street[];
  average_congestion: number;
  parking_zones: ParkingZone[];
  total_parking_spots: number;
  total_free_spots: number;
  emergency_vehicles: any[];
  active_emergencies: number;
}

// Traffic Street
interface Street {
  street_id: string;          // "street_1", "street_2", etc.
  street_name: string;         // "Main Intersection - North"
  congestion_score: number;    // 0.0 to 1.0 (0% to 100%)
  congestion_level: string;    // "low" | "medium" | "high" | "critical"
  coordinates: number[][];     // [[lon, lat], [lon, lat]]
  max_speed: number;           // Speed limit (km/h)
}

// Parking Zone
interface ParkingZone {
  zone_id: string;         // "zone_A", "zone_B"
  zone_name: string;       // "Central Parking Lot"
  total_spots: number;     // 10
  free_spots: number;      // 4
  occupancy_rate: number;  // 0.6 (60%)
  latitude: number;
  longitude: number;
  spots: ParkingSpot[];
}

// Individual Parking Spot
interface ParkingSpot {
  spot_id: string;   // "SPOT_A1"
  status: string;    // "occupied" | "free"
}
```

---

## 🎨 Color Schemes

### Traffic Congestion Colors

```javascript
function getCongestionColor(score) {
  if (score < 0.4) return '#00FF00';  // 🟢 Green (0-40%)
  if (score < 0.6) return '#FFFF00';  // 🟡 Yellow (40-60%)
  if (score < 0.8) return '#FFA500';  // 🟠 Orange (60-80%)
  return '#FF0000';                   // 🔴 Red (80-100%)
}

function getCongestionLabel(level) {
  const labels = {
    'low': { color: '#00FF00', icon: '🟢', text: 'Low Traffic' },
    'medium': { color: '#FFFF00', icon: '🟡', text: 'Moderate' },
    'high': { color: '#FFA500', icon: '🟠', text: 'Heavy' },
    'critical': { color: '#FF0000', icon: '🔴', text: 'Gridlock' }
  };
  return labels[level];
}
```

### Parking Status Colors

```javascript
function getParkingColor(occupancy_rate) {
  if (occupancy_rate < 0.5) return '#00FF00';  // 🟢 Green (< 50% full)
  if (occupancy_rate < 0.8) return '#FFFF00';  // 🟡 Yellow (50-80% full)
  return '#FF0000';                            // 🔴 Red (> 80% full)
}
```

---

## 🔄 Real-Time Updates

**Recommended approach:** Poll every 2 seconds

```javascript
// Fetch live status
async function fetchLiveStatus() {
  const response = await fetch('http://localhost:8000/api/v1/status/live');
  const data = await response.json();
  return data;
}

// Update every 2 seconds
setInterval(async () => {
  const status = await fetchLiveStatus();
  updateDashboard(status);
}, 2000);
```

---

## 🗺️ UI Components to Build

### 1. Traffic Map (Priority 1)

**Display:**
- Interactive map with 4 streets
- Each street as colored line (based on congestion)
- Street name labels
- Congestion percentage
- Last update timestamp

**Example:**
```
🗺️ Traffic Map
━━━━━━━━━━━━━━━━━━━━━
Street 1: ████░░░░░░ 21% 🟢
Street 2: █████░░░░░ 55% 🟡
Street 3: ████████░░ 80% 🟠
Street 4: ███░░░░░░░ 30% 🟢
━━━━━━━━━━━━━━━━━━━━━
Avg: 44% 🟡
```

### 2. Parking Dashboard (Priority 1)

**Display:**
- List of parking zones
- Total/occupied/free spots
- Occupancy percentage
- Visual grid of spots (green = free, red = occupied)

**Example:**
```
🅿️ Parking Zones
━━━━━━━━━━━━━━━━━━━━━
Zone A: Central Parking Lot
[■■■■■■□□□□] 60% Full
6/10 occupied • 4 free

Zone B: North Parking Area  
[■■■■■■■■□□] 80% Full
5/8 occupied • 3 free
━━━━━━━━━━━━━━━━━━━━━
Total: 7/18 spots available
```

### 3. Statistics Panel (Priority 2)

**Display:**
- Average city congestion
- Total parking availability
- Active emergencies

**Example:**
```
📊 City Statistics
━━━━━━━━━━━━━━━━━━━━━
Avg Traffic: 44% 🟡
Parking Free: 7/18 spots
Emergencies: 0 ✅
━━━━━━━━━━━━━━━━━━━━━
```

---

## 🎯 Minimal MVP (Start Here!)

### Step 1: Fetch Data

```javascript
const data = await fetch('http://localhost:8000/api/v1/status/live')
  .then(res => res.json());
```

### Step 2: Display Streets

```jsx
{data.streets.map(street => (
  <div key={street.street_id}>
    <h3>{street.street_name}</h3>
    <div style={{
      width: '100%',
      height: '20px',
      background: getCongestionColor(street.congestion_score)
    }}>
      {Math.round(street.congestion_score * 100)}%
    </div>
  </div>
))}
```

### Step 3: Display Parking

```jsx
{data.parking_zones.map(zone => (
  <div key={zone.zone_id}>
    <h3>{zone.zone_name}</h3>
    <p>{zone.free_spots}/{zone.total_spots} spots available</p>
    <div>
      {zone.spots.map(spot => (
        <span key={spot.spot_id} style={{
          display: 'inline-block',
          width: '20px',
          height: '20px',
          background: spot.status === 'free' ? '#00FF00' : '#FF0000',
          margin: '2px'
        }} />
      ))}
    </div>
  </div>
))}
```

---

## 🛠️ Development Tips

### CORS is Already Enabled

The backend allows requests from `localhost`. No CORS issues!

### Map Libraries

**Recommended:**
- Leaflet.js (simple, free)
- Mapbox (beautiful, free tier)

**Example with Leaflet:**

```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
const map = L.map('map').setView([40.7589, -73.9762], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Draw street
const street = data.streets[0];
const polyline = L.polyline(
  street.coordinates.map(([lon, lat]) => [lat, lon]),
  { color: getCongestionColor(street.congestion_score) }
).addTo(map);
</script>
```

### Testing

```bash
# Test the endpoint
curl http://localhost:8000/api/v1/status/live | jq

# Start backend
cd Heaven && docker-compose up -d

# Check API docs
open http://localhost:8000/docs
```

---

## 📐 UI Layout Suggestion

```
┌─────────────────────────────────────────────────────────┐
│  UrbanFlowAI Dashboard                            [⚙️]  │
├──────────────────────────┬──────────────────────────────┤
│                          │  📊 STATISTICS               │
│   🗺️ TRAFFIC MAP         │  ┌────────────────────────┐ │
│  ┌────────────────────┐  │  │ Avg Congestion: 44%   │ │
│  │                    │  │  │ Parking Free: 7/18    │ │
│  │  [Map with colored │  │  │ Emergencies: 0        │ │
│  │   street lines]    │  │  └────────────────────────┘ │
│  │                    │  │                              │
│  │ Legend:            │  │  🅿️ PARKING ZONES           │
│  │ 🟢 Low (0-40%)     │  │  ┌────────────────────────┐ │
│  │ 🟡 Medium (40-60%) │  │  │ Zone A: Central        │ │
│  │ 🟠 High (60-80%)   │  │  │ [■■■■■■□□□□] 60%      │ │
│  │ 🔴 Critical (80%+) │  │  │                        │ │
│  └────────────────────┘  │  │ Zone B: North          │ │
│                          │  │ [■■■■■■■■□□] 80%      │ │
│  🔄 Updated: 2s ago      │  └────────────────────────┘ │
└──────────────────────────┴──────────────────────────────┘
```

---

## ✅ Quick Checklist

- [ ] Fetch `/api/v1/status/live` every 2 seconds
- [ ] Display 4 streets with color-coded congestion
- [ ] Show street names and percentages
- [ ] Display 2 parking zones
- [ ] Show occupied/free spots count
- [ ] Visual grid of parking spots (green/red)
- [ ] Statistics panel (avg congestion, parking)
- [ ] Responsive design
- [ ] Loading states
- [ ] Error handling

---

## 🚀 Start Backend

```bash
cd Heaven
docker-compose up -d
```

**API will be available at:** `http://localhost:8000`

---

## 📞 Need Help?

- **API Docs:** http://localhost:8000/docs
- **Full Guide:** See `docs/FOR_DEVELOPERS.md`
- **Test Endpoint:** `curl http://localhost:8000/api/v1/status/live`

---

**That's it! You have everything you need to build the UI!** 🎉

---

---

# 🎨 DETAILED UI/UX DESIGN SPECIFICATION

## 🎯 Overview

Build a **modern, responsive, real-time dashboard** for urban traffic management. The design should be **professional, clean, and data-focused** with smooth animations and clear visual hierarchy.

---

## 🌈 Design System

### Color Palette

**Primary Colors:**
```css
--primary-bg: #0f172a;        /* Dark slate background */
--secondary-bg: #1e293b;      /* Lighter slate for cards */
--accent-blue: #3b82f6;       /* Primary accent */
--accent-cyan: #06b6d4;       /* Secondary accent */
--text-primary: #f8fafc;      /* White text */
--text-secondary: #94a3b8;    /* Gray text */
--border-color: #334155;      /* Subtle borders */
```

**Status Colors:**
```css
--success-green: #10b981;     /* Low congestion, free spots */
--warning-yellow: #f59e0b;    /* Medium congestion */
--danger-orange: #f97316;     /* High congestion */
--critical-red: #ef4444;      /* Critical congestion */
--info-blue: #3b82f6;         /* Information */
```

**Gradients:**
```css
--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--gradient-success: linear-gradient(135deg, #10b981 0%, #059669 100%);
--gradient-warning: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
--gradient-danger: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
```

### Typography

**Font Family:**
```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'Fira Code', 'Courier New', monospace;
```

**Font Sizes:**
```css
--text-xs: 0.75rem;    /* 12px - Small labels */
--text-sm: 0.875rem;   /* 14px - Body text */
--text-base: 1rem;     /* 16px - Default */
--text-lg: 1.125rem;   /* 18px - Card titles */
--text-xl: 1.25rem;    /* 20px - Section headers */
--text-2xl: 1.5rem;    /* 24px - Page title */
--text-3xl: 1.875rem;  /* 30px - Hero text */
```

**Font Weights:**
```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Spacing

```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
```

### Border Radius

```css
--radius-sm: 0.375rem;   /* 6px - Small elements */
--radius-md: 0.5rem;     /* 8px - Cards */
--radius-lg: 0.75rem;    /* 12px - Large cards */
--radius-xl: 1rem;       /* 16px - Hero sections */
--radius-full: 9999px;   /* Circular */
```

### Shadows

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
--shadow-glow: 0 0 20px rgba(59, 130, 246, 0.3);
```

---

## 📐 Layout Structure

### Grid System

**Desktop (1920x1080):**
```
┌─────────────────────────────────────────────────────────────┐
│  Header (80px height, full width)                           │
├──────────────────────────┬──────────────────────────────────┤
│                          │                                  │
│  Map Section             │  Right Sidebar                   │
│  (70% width)             │  (30% width)                     │
│  Min: 800px              │  Min: 400px                      │
│                          │                                  │
│  - Traffic Map           │  - Statistics Card               │
│  - Interactive Controls  │  - Parking Zones (scrollable)    │
│  - Legend                │  - Activity Feed                 │
│                          │                                  │
│  Height: calc(100vh-80px)│  Height: calc(100vh-80px)        │
│                          │  Overflow-y: auto                │
│                          │                                  │
└──────────────────────────┴──────────────────────────────────┘
```

**Tablet (768px - 1024px):**
```
┌─────────────────────────────────────┐
│  Header (70px height)               │
├─────────────────────────────────────┤
│  Map Section (100% width)           │
│  Height: 50vh                       │
├─────────────────────────────────────┤
│  Sidebar Content (100% width)       │
│  - Statistics (horizontal cards)    │
│  - Parking Zones (2 columns)        │
│  Overflow-y: scroll                 │
└─────────────────────────────────────┘
```

**Mobile (< 768px):**
```
┌───────────────────────────┐
│  Header (60px, fixed)     │
├───────────────────────────┤
│  Quick Stats (compact)    │
├───────────────────────────┤
│  Tabs: [Map | Parking]    │
├───────────────────────────┤
│                           │
│  Active Tab Content       │
│  (full width, scrollable) │
│                           │
│                           │
└───────────────────────────┘
```

---

## 🎨 Component Specifications

### 1. Header / Navigation Bar

**Dimensions:**
- Height: 80px (desktop), 70px (tablet), 60px (mobile)
- Padding: 0 32px (desktop), 0 24px (tablet), 0 16px (mobile)
- Background: `var(--secondary-bg)` with `backdrop-filter: blur(10px)`
- Border bottom: 1px solid `var(--border-color)`
- Position: Fixed top, z-index: 1000

**Content:**
```
┌─────────────────────────────────────────────────────────┐
│ [🚦 Logo] UrbanFlowAI     [🔔 Alerts: 0] [⚙️ Settings]  │
│                                                         │
│ Real-Time Traffic & Parking Management                 │
└─────────────────────────────────────────────────────────┘
```

**Logo:**
- Icon: 🚦 or custom traffic light SVG
- Text: "UrbanFlowAI" in `--text-2xl`, `--font-bold`
- Color: Gradient text from `--accent-blue` to `--accent-cyan`

**Status Indicator:**
- Live dot: Pulsing green circle (8px diameter)
- Text: "LIVE" in `--text-xs`, `--font-semibold`
- Animation: Pulse every 2s

**Last Updated:**
- Text: "Updated 2s ago"
- Color: `--text-secondary`
- Font: `--text-sm`
- Auto-refresh indicator

**Settings Button:**
- Icon: ⚙️ or settings SVG
- Size: 40px x 40px
- Hover: Rotate 90deg, scale(1.1)
- Background: Transparent → `var(--accent-blue)` on hover

---

### 2. Statistics Dashboard (Top Right)

**Card Design:**
```
┌─────────────────────────────────────────┐
│  📊 City Overview             🟢 LIVE   │
├─────────────────────────────────────────┤
│                                         │
│  Average Congestion                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━     │
│  ██████████████░░░░░░░░░░░░░░░░  44%   │
│  🟡 MODERATE                            │
│                                         │
│  ─────────────────────────────────      │
│                                         │
│  🚗 Total Vehicles: 53                  │
│  🅿️  Available Parking: 7/18 spots      │
│  🚨 Active Emergencies: 0               │
│                                         │
└─────────────────────────────────────────┘
```

**Styling:**
- Background: `var(--secondary-bg)`
- Border: 1px solid `var(--border-color)`
- Border radius: `var(--radius-lg)`
- Padding: `var(--space-6)`
- Shadow: `var(--shadow-lg)`
- Margin bottom: `var(--space-6)`

**Congestion Bar:**
- Height: 32px
- Background: Linear gradient based on level
- Border radius: `var(--radius-md)`
- Animated fill on update (transition: 0.5s ease)
- Text overlay: White, `--font-bold`

**Stat Items:**
- Icon: 24px, colored by status
- Label: `--text-base`, `--text-secondary`
- Value: `--text-xl`, `--font-semibold`, `--text-primary`
- Spacing: `var(--space-4)` between items

---

### 3. Traffic Map Section

**Map Container:**
```
┌─────────────────────────────────────────────────┐
│  🗺️ Live Traffic Map                           │
├─────────────────────────────────────────────────┤
│                                                 │
│  [Interactive Leaflet/Mapbox Map]              │
│                                                 │
│  Features:                                      │
│  - 4 colored street lines                      │
│  - Tooltips on hover                           │
│  - Zoom controls (bottom right)                │
│  - Legend (bottom left)                        │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Map Styling:**
- Use dark map theme (Mapbox Dark or similar)
- Background: `#0f172a` (matches app background)
- Border radius: `var(--radius-lg)`
- Shadow: `var(--shadow-xl)`

**Street Lines:**
- Width: 6px (default), 8px (hover), 10px (selected)
- Opacity: 0.8 (default), 1.0 (hover)
- Cap: round
- Join: round
- Transition: All 0.3s ease

**Street Colors by Congestion:**
- Low (0-40%): `#10b981` → `#059669` gradient
- Medium (40-60%): `#f59e0b` → `#d97706` gradient
- High (60-80%): `#f97316` → `#ea580c` gradient
- Critical (80-100%): `#ef4444` → `#dc2626` gradient

**Tooltip on Street Hover:**
```
┌────────────────────────────┐
│ Main Intersection - North  │
│ ──────────────────────     │
│ Congestion: 21%  🟢       │
│ Status: Low Traffic        │
│ Speed Limit: 50 km/h       │
│ Vehicles: 12               │
└────────────────────────────┘
```

**Tooltip Styling:**
- Background: `rgba(30, 41, 59, 0.95)`
- Border: 1px solid `var(--border-color)`
- Border radius: `var(--radius-md)`
- Padding: `var(--space-3)`
- Font: `--text-sm`
- Shadow: `var(--shadow-lg)`
- Arrow pointing to street
- Fade in: 0.2s

**Map Legend (Bottom Left):**
```
┌─────────────────────────┐
│  Traffic Levels         │
│  ─────────────────      │
│  ━━ Low (0-40%)    🟢   │
│  ━━ Medium (40-60%) 🟡  │
│  ━━ High (60-80%)   🟠  │
│  ━━ Critical (80%+) 🔴  │
└─────────────────────────┘
```

**Legend Styling:**
- Position: Absolute, bottom: 20px, left: 20px
- Background: `rgba(30, 41, 59, 0.9)`
- Backdrop filter: blur(10px)
- Border: 1px solid `var(--border-color)`
- Border radius: `var(--radius-md)`
- Padding: `var(--space-4)`
- Font: `--text-sm`

---

### 4. Parking Zones Section

**Zone Card Design:**
```
┌──────────────────────────────────────────┐
│  🅿️  Central Parking Lot       🟡 60%    │
├──────────────────────────────────────────┤
│                                          │
│  6 occupied • 4 available                │
│                                          │
│  [■][■][■][■][■][■][□][□][□][□]         │
│                                          │
│  ──────────────────────────────────      │
│  Location: 40.7589, -73.9762            │
│  Last updated: 2s ago                    │
│                                          │
└──────────────────────────────────────────┘
```

**Card Styling:**
- Background: `var(--secondary-bg)`
- Border: 2px solid (color based on occupancy)
  - < 50%: `var(--success-green)`
  - 50-80%: `var(--warning-yellow)`
  - > 80%: `var(--critical-red)`
- Border radius: `var(--radius-lg)`
- Padding: `var(--space-5)`
- Margin bottom: `var(--space-4)`
- Hover: Lift effect (transform: translateY(-4px), shadow increases)
- Transition: All 0.3s ease

**Header:**
- Title: `--text-lg`, `--font-semibold`
- Icon: 24px parking sign
- Percentage badge: 
  - Position: Absolute, top right
  - Size: 60px x 32px
  - Border radius: `var(--radius-full)`
  - Background: Color based on occupancy
  - Font: `--text-base`, `--font-bold`
  - Pulse animation on update

**Stats Row:**
- Font: `--text-sm`, `--text-secondary`
- Icons: 16px
- Spacing: `var(--space-2)`

**Parking Spots Grid:**
- Display: Grid
- Grid template columns: repeat(10, 1fr)
- Gap: `var(--space-2)`
- Margin: `var(--space-4)` 0

**Individual Spot:**
- Size: 32px x 32px (desktop), 28px x 28px (mobile)
- Border radius: `var(--radius-sm)`
- Border: 2px solid `var(--border-color)`
- Background:
  - Occupied: `var(--critical-red)`
  - Free: `var(--success-green)`
- Transition: All 0.3s ease
- Hover: Scale(1.1), show spot ID tooltip
- Animation on status change: Pulse + color fade

**Spot Hover Tooltip:**
```
┌─────────────┐
│  SPOT_A3    │
│  Occupied   │
└─────────────┘
```

**Location Row:**
- Font: `--text-xs`, `--font-mono`
- Color: `--text-secondary`
- Icon: 📍 (12px)

---

### 5. Real-Time Activity Feed (Optional Enhancement)

```
┌─────────────────────────────────────────┐
│  📡 Live Activity Feed                  │
├─────────────────────────────────────────┤
│                                         │
│  [2s ago] Street 2 congestion → 55% 🟡  │
│  [5s ago] Zone A: SPOT_A3 → occupied    │
│  [8s ago] Street 3 congestion → 78% 🟠  │
│  [12s ago] Zone B: SPOT_B5 → free       │
│  [15s ago] Street 1 congestion → 21% 🟢 │
│                                         │
│  [View All Activity →]                  │
│                                         │
└─────────────────────────────────────────┘
```

**Feed Styling:**
- Background: `var(--secondary-bg)`
- Border: 1px solid `var(--border-color)`
- Border radius: `var(--radius-lg)`
- Padding: `var(--space-5)`
- Max height: 400px
- Overflow-y: auto

**Activity Item:**
- Padding: `var(--space-3)` 0
- Border bottom: 1px solid `var(--border-color)`
- Font: `--text-sm`
- Timestamp: `--text-secondary`, `--font-mono`
- Event: `--text-primary`
- Icon: Status emoji (16px)
- Fade in animation when new item appears
- Slide down from top

---

## 🎬 Animations & Transitions

### Loading States

**Initial Page Load:**
```
1. Skeleton screens (0-0.5s)
   - Gray pulsing placeholders for all cards
   
2. Fade in content (0.5-1s)
   - Cards appear with stagger delay
   - Delay: 0.1s between each card
   
3. Data population (1-1.5s)
   - Numbers count up from 0
   - Bars fill from left to right
```

**Data Refresh (Every 2s):**
```
1. Subtle pulse (0.1s)
   - Card border glows briefly
   
2. Update values (0.3s)
   - Numbers: Morph animation
   - Bars: Smooth fill/drain
   - Colors: Fade transition
   
3. Ripple effect (0.2s)
   - Small wave from updated element
```

### Micro-interactions

**Button Hover:**
```css
transition: all 0.2s ease;
transform: scale(1.05);
box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
```

**Card Hover:**
```css
transition: all 0.3s ease;
transform: translateY(-4px);
box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
```

**Street Line Hover:**
```css
transition: all 0.3s ease;
stroke-width: 10px;
opacity: 1;
filter: drop-shadow(0 0 10px currentColor);
```

**Parking Spot Click:**
```css
animation: spotClick 0.4s ease;
@keyframes spotClick {
  0% { transform: scale(1); }
  50% { transform: scale(1.3) rotate(5deg); }
  100% { transform: scale(1); }
}
```

### Status Change Animations

**Congestion Increase:**
- Bar extends with gradient sweep
- Color transitions smoothly
- Number counts up
- Badge pulses 3 times

**Parking Spot Changes:**
- Occupied: Red ripple from center
- Free: Green burst from center
- Duration: 0.5s
- Easing: cubic-bezier(0.34, 1.56, 0.64, 1)

---

## 📱 Responsive Breakpoints

```css
/* Mobile Small */
@media (max-width: 480px) {
  --text-2xl: 1.25rem;
  --space-6: 1rem;
  /* Single column layout */
  /* Collapsible sections */
  /* Bottom navigation */
}

/* Mobile Large */
@media (min-width: 481px) and (max-width: 767px) {
  /* Single column */
  /* Tabs for map/parking switch */
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1023px) {
  /* Stacked layout */
  /* Map on top (50vh) */
  /* Sidebar below (scrollable) */
}

/* Desktop Small */
@media (min-width: 1024px) and (max-width: 1439px) {
  /* Side-by-side layout */
  /* Map: 65%, Sidebar: 35% */
}

/* Desktop Large */
@media (min-width: 1440px) {
  /* Side-by-side layout */
  /* Map: 70%, Sidebar: 30% */
  /* Larger fonts and spacing */
}

/* Ultra-wide */
@media (min-width: 1920px) {
  /* Max content width: 1920px */
  /* Centered layout */
  /* Extra padding */
}
```

---

## ♿ Accessibility

**ARIA Labels:**
```html
<div role="main" aria-label="Traffic Dashboard">
  <section aria-label="Live Traffic Map" aria-live="polite">
  <section aria-label="Parking Zones" aria-live="polite">
  <div role="status" aria-label="City Statistics">
```

**Keyboard Navigation:**
- Tab through all interactive elements
- Arrow keys to navigate map
- Enter/Space to interact
- Escape to close modals/tooltips

**Screen Reader Support:**
- Announce updates: "Street 2 congestion increased to 55%"
- Describe status: "Zone A parking 60% occupied, 4 spots available"
- Alternative text for all icons

**Color Contrast:**
- Text on background: Minimum 4.5:1 ratio
- Interactive elements: Minimum 3:1 ratio
- Use icons + colors (not just colors)

**Focus States:**
```css
:focus-visible {
  outline: 2px solid var(--accent-blue);
  outline-offset: 2px;
}
```

---

## 🚀 Performance Optimizations

**Loading Strategy:**
1. Critical CSS inline in `<head>`
2. Lazy load map library
3. Preload font files
4. Defer non-critical JS

**Update Strategy:**
```javascript
// Debounce rapid updates
const debouncedUpdate = debounce(updateUI, 100);

// Virtual scrolling for long lists
// Memoize expensive calculations
// Use React.memo / useMemo

// Batch DOM updates
requestAnimationFrame(() => {
  updateStreets();
  updateParking();
  updateStats();
});
```

**Asset Optimization:**
- SVG icons (not PNGs)
- WebP images with fallbacks
- Compressed fonts (woff2)
- Minified CSS/JS
- Gzip/Brotli compression

---

## 🎨 Advanced Visual Effects

### Glassmorphism (for cards)

```css
.card {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### Gradient Borders

```css
.highlight-card {
  border: 2px solid transparent;
  background: linear-gradient(var(--secondary-bg), var(--secondary-bg)) padding-box,
              linear-gradient(135deg, #667eea, #764ba2) border-box;
}
```

### Pulsing Status Indicator

```css
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

.live-indicator {
  animation: pulse 2s ease-in-out infinite;
}
```

### Data Visualization Glow

```css
.congestion-bar {
  box-shadow: 0 0 20px currentColor;
  animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
  from { box-shadow: 0 0 10px currentColor; }
  to { box-shadow: 0 0 20px currentColor; }
}
```

---

## 🖼️ Example Component Code

### Congestion Bar Component (React)

```jsx
const CongestionBar = ({ score, level }) => {
  const getColor = () => {
    if (score < 0.4) return '#10b981';
    if (score < 0.6) return '#f59e0b';
    if (score < 0.8) return '#f97316';
    return '#ef4444';
  };

  const getIcon = () => {
    const icons = {
      low: '🟢',
      medium: '🟡',
      high: '🟠',
      critical: '🔴'
    };
    return icons[level] || '⚪';
  };

  return (
    <div className="congestion-bar-container">
      <div className="congestion-label">
        <span>Average Congestion</span>
        <span className="congestion-icon">{getIcon()}</span>
      </div>
      
      <div className="congestion-bar-track">
        <div 
          className="congestion-bar-fill"
          style={{
            width: `${score * 100}%`,
            background: getColor(),
            transition: 'all 0.5s ease'
          }}
        >
          <span className="congestion-value">{Math.round(score * 100)}%</span>
        </div>
      </div>
      
      <div className="congestion-status">{level.toUpperCase()}</div>
    </div>
  );
};
```

### Parking Spot Grid Component (React)

```jsx
const ParkingSpotGrid = ({ spots }) => {
  return (
    <div className="parking-grid">
      {spots.map(spot => (
        <div
          key={spot.spot_id}
          className={`parking-spot ${spot.status}`}
          title={`${spot.spot_id}: ${spot.status}`}
          style={{
            backgroundColor: spot.status === 'free' ? '#10b981' : '#ef4444',
            animation: 'spotUpdate 0.5s ease'
          }}
        >
          {/* Optional: Show spot number */}
        </div>
      ))}
    </div>
  );
};
```

---

## 📋 Implementation Checklist

### Phase 1: Core UI (Day 1)
- [ ] Setup React/Vue project with Tailwind CSS
- [ ] Create base layout (header + main grid)
- [ ] Implement dark theme with design tokens
- [ ] Build statistics dashboard card
- [ ] Create parking zone cards with spot grids
- [ ] Add loading skeletons

### Phase 2: Map Integration (Day 2)
- [ ] Integrate Leaflet/Mapbox
- [ ] Draw 4 streets as colored polylines
- [ ] Add interactive tooltips on hover
- [ ] Implement map legend
- [ ] Add zoom/pan controls
- [ ] Make map responsive

### Phase 3: Real-Time Updates (Day 3)
- [ ] Setup API polling (2s interval)
- [ ] Connect data to UI components
- [ ] Implement smooth transitions on update
- [ ] Add status change animations
- [ ] Show "last updated" timestamps
- [ ] Add live status indicator

### Phase 4: Polish & UX (Day 4)
- [ ] Add micro-interactions (hover, click)
- [ ] Implement all animations
- [ ] Add loading states
- [ ] Error handling & retry logic
- [ ] Optimize performance
- [ ] Test on mobile/tablet
- [ ] Accessibility audit
- [ ] Cross-browser testing

---

## 🎯 Key Success Metrics

**Visual Quality:**
- ✅ Professional, modern design
- ✅ Consistent spacing and alignment
- ✅ Smooth animations (60fps)
- ✅ No layout shifts or jank

**Functionality:**
- ✅ Real-time updates every 2s
- ✅ All data displays correctly
- ✅ Interactive map works smoothly
- ✅ Responsive on all devices

**Performance:**
- ✅ First paint < 1s
- ✅ Time to interactive < 2s
- ✅ Smooth scrolling (60fps)
- ✅ Low memory usage

**Accessibility:**
- ✅ WCAG 2.1 AA compliance
- ✅ Keyboard navigation works
- ✅ Screen reader compatible
- ✅ Sufficient color contrast

---

**With these detailed specifications, you can build a world-class UI! 🎨🚀**

