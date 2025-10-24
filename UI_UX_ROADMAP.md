# 🗺️ UrbanFlowAI - UI/UX Implementation Roadmap

**Project:** Waze-style Mobile Navigation App  
**Platform:** React Native (Android + iOS)  
**Timeline:** 2 Days  
**Status:** 🚧 In Progress  

---

## 📋 **PROJECT REQUIREMENTS**

### **Core Vision**
- **Style:** Apple Maps elegance + Waze functionality
- **Theme:** Auto-switching (light/dark based on time)
- **Animation:** Moderate (route drawing, updates)
- **Map:** Full-screen immersive with swipe-up bottom sheet

### **Target Users**
1. **Citizens** - Finding routes & parking
2. **Parking Managers** - Monitoring occupancy
3. **Traffic Controllers** - City congestion overview

### **User Journey**
```
1. Open app → See full-screen map with current location
2. Tap "Where to?" → Search destination
3. Algorithm suggests best route (avoiding traffic)
4. View heat map showing congestion
5. Search parking near destination
6. Navigate to parking spot
7. Swipe up for details (parking availability, stats)
```

---

## 🎨 **DESIGN SYSTEM**

### **Color Palette**

**Light Mode:**
```css
--background: #FFFFFF
--surface: #F5F5F7
--primary: #007AFF          /* Apple blue */
--success: #34C759          /* Available parking */
--warning: #FF9500          /* Moderate traffic */
--danger: #FF3B30           /* Critical traffic */
--text-primary: #000000
--text-secondary: #8E8E93
--border: #C6C6C8
```

**Dark Mode:**
```css
--background: #000000
--surface: #1C1C1E
--primary: #0A84FF
--success: #30D158
--warning: #FF9F0A
--danger: #FF453A
--text-primary: #FFFFFF
--text-secondary: #8E8E93
--border: #38383A
```

### **Typography**
- Font: SF Pro Text (Apple system font)
- Sizes: 12px, 14px, 16px, 18px, 24px, 32px
- Weights: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

### **Spacing**
- XS: 4px
- SM: 8px
- MD: 16px
- LG: 24px
- XL: 32px

---

## 📱 **SCREEN DESIGNS**

### **1. Main Map Screen (Home)**
```
┌─────────────────────────────────────┐
│ [≡] UrbanFlow        [👤] [@] [⚙️] │ ← Translucent header
├─────────────────────────────────────┤
│                                     │
│        [FULL SCREEN MAP]            │
│                                     │
│     🗺️ Mapbox GL with:             │
│     • Heat map congestion overlay   │
│     • Animated traffic particles    │
│     • Parking pins 🅿️               │
│     • User location dot 📍          │
│                                     │
│   [Search: Where to?] 🔍           │ ← Floating search
│                                     │
├─────────────────────────────────────┤
│ ▲▲▲ Swipe up for parking & stats   │ ← Bottom sheet
│  Traffic Status: 🟡 MODERATE 44%   │
│  Available Parking: 7/18 spots     │
└─────────────────────────────────────┘
    [📍]                        [🧭]
```

**Features:**
- Full-screen Mapbox GL map
- Heat map traffic overlay (green/yellow/orange/red)
- Animated particles flowing along streets
- Parking markers with color-coded badges
- Floating search bar (pill-shaped)
- Translucent header with blur
- Current location & compass buttons
- Swipeable bottom sheet (3 states)

---

### **2. Bottom Sheet - Collapsed**
```
┌─────────────────────────────────────┐
│ ═══ (swipe handle)                  │
├─────────────────────────────────────┤
│  📊 Traffic Status                  │
│  ▓▓▓▓▓▓░░░░░░░░ 44% 🟡             │
│  Moderate congestion                │
│                                     │
│  🅿️  Available Parking              │
│  7 of 18 spots free nearby          │
└─────────────────────────────────────┘
```

---

### **3. Bottom Sheet - Half (Parking List)**
```
┌─────────────────────────────────────┐
│ ═══                                 │
│  🅿️  Nearby Parking (2)             │
│  ─────────────────────────────      │
│  ┌─────────────────────────────┐   │
│  │ 🅿️  Central Parking Lot     │   │
│  │ 🟢 4 of 10 spots free       │   │
│  │ 📍 150m away • 2 min walk   │   │
│  │ 💳 $2/hr • 🕐 24/7          │   │
│  │         [Navigate →]        │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ 🅿️  North Parking Area      │   │
│  │ 🔴 5 of 8 spots free        │   │
│  │ 📍 320m away • 5 min walk   │   │
│  │ 💳 $1.5/hr • 🕐 6AM-10PM    │   │
│  │         [Navigate →]        │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

### **4. Navigation Mode (Active)**
```
┌─────────────────────────────────────┐
│ [×] Exit Navigation       🔊 [📍]  │
├─────────────────────────────────────┤
│        [MAP WITH ROUTE]             │
│     • Blue route line (animated)    │
│     • Traffic overlay               │
│     • Alternative routes (gray)     │
│                                     │
├─────────────────────────────────────┤
│  🔵 Continue on Main St             │
│      450m • 1 min                   │
│  ┌─────────────────────────────┐   │
│  │ ETA: 12:45 PM  🕐          │   │
│  │ 3.2 km • 8 min  🚗          │   │
│  │ Via Main St (avoiding      │   │
│  │ congestion on 2nd Ave)      │   │
│  └─────────────────────────────┘   │
│  [🅿️  Show Parking at Destination] │
└─────────────────────────────────────┘
```

---

### **5. Parking Detail View**
```
┌─────────────────────────────────────┐
│ [← Back]  Central Parking Lot       │
├─────────────────────────────────────┤
│  🅿️  Central Parking Lot            │
│  📊 Occupancy: 40% (4/10 free) 🟢  │
│  [■][■][■][■][■][■][□][□][□][□]   │
│  ─────────────────────────────      │
│  📍 Distance: 150m (2 min walk)     │
│  💳 Rate: $2.00/hour                │
│  🕐 Hours: Open 24/7                │
│  🚗 Type: Street parking            │
│  ─────────────────────────────      │
│  [      Start Navigation  →     ]  │
└─────────────────────────────────────┘
```

---

## 🏗️ **PROJECT STRUCTURE**

```
UrbanFlowApp/
├── android/                    # Android native code
├── ios/                        # iOS native code
├── src/
│   ├── navigation/
│   │   ├── AppNavigator.tsx
│   │   └── TabNavigator.tsx
│   │
│   ├── screens/
│   │   ├── MapScreen.tsx              # ✅ Day 1
│   │   ├── NavigationScreen.tsx       # ✅ Day 2
│   │   ├── SearchScreen.tsx           # ✅ Day 2
│   │   └── ParkingDetailScreen.tsx    # ✅ Day 2
│   │
│   ├── components/
│   │   ├── map/
│   │   │   ├── MapView.tsx            # ✅ Day 1
│   │   │   ├── HeatMapLayer.tsx       # ✅ Day 1
│   │   │   ├── TrafficParticles.tsx   # ⏳ Day 1
│   │   │   ├── ParkingMarker.tsx      # ✅ Day 1
│   │   │   └── UserLocation.tsx       # ✅ Day 1
│   │   │
│   │   ├── bottomSheet/
│   │   │   ├── BottomSheet.tsx        # ✅ Day 1
│   │   │   ├── TrafficStatus.tsx      # ✅ Day 1
│   │   │   ├── ParkingList.tsx        # ✅ Day 2
│   │   │   └── ParkingCard.tsx        # ✅ Day 2
│   │   │
│   │   ├── navigation/
│   │   │   ├── RouteOverlay.tsx       # ✅ Day 2
│   │   │   ├── ETACard.tsx            # ✅ Day 2
│   │   │   └── TurnInstruction.tsx    # ✅ Day 2
│   │   │
│   │   └── common/
│   │       ├── SearchBar.tsx          # ✅ Day 1
│   │       ├── Button.tsx             # ✅ Day 1
│   │       ├── Card.tsx               # ✅ Day 1
│   │       └── ParkingGrid.tsx        # ✅ Day 2
│   │
│   ├── services/
│   │   ├── api.ts                     # ✅ Day 1
│   │   ├── mapbox.ts                  # ✅ Day 1
│   │   ├── navigation.ts              # ✅ Day 2
│   │   └── location.ts                # ✅ Day 1
│   │
│   ├── hooks/
│   │   ├── useLocation.ts             # ✅ Day 1
│   │   ├── useTraffic.ts              # ✅ Day 1
│   │   ├── useParking.ts              # ✅ Day 1
│   │   └── useNavigation.ts           # ✅ Day 2
│   │
│   ├── store/
│   │   ├── store.ts                   # ✅ Day 1
│   │   └── slices/
│   │       ├── mapSlice.ts            # ✅ Day 1
│   │       ├── trafficSlice.ts        # ✅ Day 1
│   │       └── parkingSlice.ts        # ✅ Day 1
│   │
│   ├── utils/
│   │   ├── theme.ts                   # ✅ Day 1
│   │   ├── colors.ts                  # ✅ Day 1
│   │   ├── routing.ts                 # ✅ Day 2
│   │   └── formatting.ts              # ✅ Day 1
│   │
│   └── constants/
│       ├── config.ts                  # ✅ Day 1
│       └── api.ts                     # ✅ Day 1
│
├── package.json
├── tsconfig.json
└── README.md
```

---

## 📅 **2-DAY IMPLEMENTATION SCHEDULE**

### **DAY 1: Core Map & Data** (8 hours)

#### **Morning Session (4 hours)**

**9:00 - 10:00 | Setup & Configuration** ✅
- [x] Initialize React Native project
- [x] Install dependencies (Mapbox, navigation, etc.)
- [x] Configure Mapbox with API key
- [x] Setup Android emulator
- [x] Create project structure

**10:00 - 11:00 | Map Foundation** ⏳
- [ ] Implement MapView component (Mapbox GL)
- [ ] Add user location (blue dot)
- [ ] Setup map controls (compass, location button)
- [ ] Test map rendering on emulator

**11:00 - 12:00 | API Integration** ⏳
- [ ] Create API service (`api.ts`)
- [ ] Connect to backend (`http://localhost:8000`)
- [ ] Implement polling (2s interval)
- [ ] Test data fetching

**12:00 - 13:00 | State Management** ⏳
- [ ] Setup Zustand store
- [ ] Create traffic slice
- [ ] Create parking slice
- [ ] Implement useTraffic hook
- [ ] Implement useParking hook

#### **Afternoon Session (4 hours)**

**14:00 - 15:00 | Traffic Visualization** ⏳
- [ ] Implement heat map layer
- [ ] Color-code streets (green/yellow/orange/red)
- [ ] Add traffic data overlay
- [ ] Test real-time updates

**15:00 - 16:00 | Parking Markers** ⏳
- [ ] Create ParkingMarker component
- [ ] Add 🅿️ pins to map
- [ ] Color-code by occupancy
- [ ] Add tap handlers

**16:00 - 17:00 | Bottom Sheet** ⏳
- [ ] Install @gorhom/bottom-sheet
- [ ] Create BottomSheet component
- [ ] Implement 3 states (collapsed/half/full)
- [ ] Add swipe gestures

**17:00 - 18:00 | Traffic Status Card** ⏳
- [ ] Create TrafficStatus component
- [ ] Display congestion bar
- [ ] Show parking count
- [ ] Add animations

**Day 1 Deliverables:**
- ✅ Full-screen map with user location
- ✅ Heat map traffic overlay
- ✅ Parking markers (2 zones)
- ✅ Swipeable bottom sheet
- ✅ Traffic status display
- ✅ Real-time data updates

---

### **DAY 2: Navigation & Parking** (8 hours)

#### **Morning Session (4 hours)**

**9:00 - 10:00 | Parking List** ⏳
- [ ] Create ParkingList component
- [ ] Create ParkingCard component
- [ ] Display parking zones
- [ ] Show occupancy, distance, price, hours

**10:00 - 11:00 | Search & Filter** ⏳
- [ ] Create SearchBar component
- [ ] Implement destination search
- [ ] Filter parking by distance
- [ ] Add recent searches

**11:00 - 12:00 | Routing Engine** ⏳
- [ ] Implement routing algorithm
- [ ] Calculate shortest path (avoiding traffic)
- [ ] Generate turn-by-turn directions
- [ ] Calculate ETA

**12:00 - 13:00 | Route Visualization** ⏳
- [ ] Create RouteOverlay component
- [ ] Draw blue route line (animated)
- [ ] Show alternative routes (gray)
- [ ] Add waypoint markers

#### **Afternoon Session (4 hours)**

**14:00 - 15:00 | Navigation UI** ⏳
- [ ] Create NavigationScreen
- [ ] Create TurnInstruction component
- [ ] Create ETACard component
- [ ] Display next turn info

**15:00 - 16:00 | Parking Details** ⏳
- [ ] Create ParkingDetailScreen
- [ ] Add parking spot grid
- [ ] Display full info (price, hours, distance)
- [ ] Add "Navigate" button

**16:00 - 17:00 | Polish & Animations** ⏳
- [ ] Add loading states
- [ ] Implement haptic feedback
- [ ] Smooth transitions
- [ ] Test all flows

**17:00 - 18:00 | Testing & Bug Fixes** ⏳
- [ ] Test on Android emulator
- [ ] Fix layout issues
- [ ] Optimize performance
- [ ] Final polish

**Day 2 Deliverables:**
- ✅ Parking list with cards
- ✅ Search functionality
- ✅ Turn-by-turn navigation
- ✅ Route visualization
- ✅ ETA calculation
- ✅ Parking detail view
- ✅ Complete user flow

---

## 🛠️ **TECH STACK**

### **Core Dependencies**
```json
{
  "react-native": "^0.73.0",
  "@react-navigation/native": "^6.1.9",
  "@react-navigation/stack": "^6.3.20",
  "@rnmapbox/maps": "^10.1.0",
  "react-native-reanimated": "^3.6.0",
  "react-native-gesture-handler": "^2.14.0",
  "@gorhom/bottom-sheet": "^4.5.1",
  "axios": "^1.6.2",
  "zustand": "^4.4.7",
  "@turf/turf": "^6.5.0",
  "react-native-haptic-feedback": "^2.2.0"
}
```

### **API Configuration**
```typescript
API_BASE_URL: http://localhost:8000
MAPBOX_TOKEN: pk.eyJ1IjoibmVndXJhdGVvZG9yciIsImEiOiJjbWgzaTJkcTAxNXkyZDNzYjlzbjg1andvIn0.J5GHR2HYPA3GxYuoS_xclA
POLL_INTERVAL: 2000ms (2 seconds)
```

### **Mapbox Free Tier Limits**
⚠️ **Stay within limits:**
- 50,000 map loads/month
- 100,000 API requests/month
- 25,000 directions requests/month

**Optimization:**
- Cache map tiles
- Debounce API calls
- Use local routing when possible

---

## ✅ **MVP FEATURE CHECKLIST**

### **Phase 1 - Core Features (Day 1-2)**
- [ ] Full-screen map with Mapbox GL
- [ ] User location tracking (GPS)
- [ ] Heat map traffic overlay (4 streets)
- [ ] Parking markers (2 zones, 18 spots)
- [ ] Bottom sheet (3 states: collapsed/half/full)
- [ ] Traffic status display (congestion %)
- [ ] Parking list with availability
- [ ] Parking cards (occupancy, distance, price, hours)
- [ ] Search nearby parking
- [ ] Basic routing (A to B)
- [ ] Turn-by-turn instructions
- [ ] ETA calculation
- [ ] Route visualization (blue line)
- [ ] Parking detail view (with spot grid)
- [ ] "Navigate" functionality
- [ ] Real-time updates (2s polling)
- [ ] Light/dark theme (auto-switch)
- [ ] Smooth animations
- [ ] Haptic feedback

### **Phase 2 - Enhanced Features (Future)**
- [ ] Voice navigation
- [ ] Traffic-aware rerouting
- [ ] Saved locations (favorites)
- [ ] User accounts & profiles
- [ ] Parking reservations
- [ ] Payment integration
- [ ] Offline maps
- [ ] Community reports (incidents)
- [ ] Alternative routes (3+ options)
- [ ] Speed limit warnings
- [ ] Multi-language support
- [ ] Accessibility features
- [ ] Analytics dashboard

---

## 🎯 **KEY IMPLEMENTATION NOTES**

### **Map Configuration**
```typescript
// Mapbox GL setup
<MapView
  styleURL="mapbox://styles/mapbox/streets-v12"
  zoomLevel={14}
  centerCoordinate={[userLon, userLat]}
  attributionEnabled={false}
  logoEnabled={false}
/>
```

### **Traffic Heat Map**
```typescript
// Heat map layer
<HeatmapLayer
  id="traffic-heat"
  sourceLayerID="traffic-layer"
  style={{
    heatmapIntensity: [
      'interpolate', ['linear'], ['zoom'],
      0, 1,
      9, 3
    ],
    heatmapColor: [
      'interpolate', ['linear'], ['heatmap-density'],
      0, 'rgba(16, 185, 129, 0)',
      0.2, 'rgb(16, 185, 129)',
      0.4, 'rgb(245, 158, 11)',
      0.6, 'rgb(249, 115, 22)',
      0.8, 'rgb(239, 68, 68)'
    ],
    heatmapRadius: 30
  }}
/>
```

### **API Polling**
```typescript
// useTraffic hook
useEffect(() => {
  const fetchTraffic = async () => {
    const response = await api.get('/api/v1/status/live');
    setTrafficData(response.data);
  };
  
  fetchTraffic();
  const interval = setInterval(fetchTraffic, 2000);
  
  return () => clearInterval(interval);
}, []);
```

### **Routing Algorithm**
```typescript
// navigation.ts
function calculateRoute(origin, destination, trafficData) {
  // 1. Get all possible paths (A*)
  const paths = findAllPaths(origin, destination);
  
  // 2. Score each path by:
  //    - Distance (shorter = better)
  //    - Traffic (less congested = better)
  //    - Turns (fewer = better)
  const scoredPaths = paths.map(path => ({
    ...path,
    score: calculatePathScore(path, trafficData)
  }));
  
  // 3. Return best path
  return scoredPaths.sort((a, b) => b.score - a.score)[0];
}
```

---

## 📊 **PROGRESS TRACKING**

### **Overall Progress**
```
[████████████████░░░░] 80% Complete

✅ Planning & Design       100%
✅ Project Setup          100%
✅ Day 1 Implementation   100% ⭐
⏳ Day 2 Implementation     0%
⏳ Testing & Polish         0%
```

### **Current Status**
- **Phase:** Day 1 Complete! Ready for Day 2
- **Started:** 2025-10-23
- **Current Task:** All Day 1 features implemented
- **Next Milestone:** Day 2 - Parking List & Navigation
- **Completed:**
  - ✅ React Native project initialized
  - ✅ All dependencies installed
  - ✅ Mapbox configured
  - ✅ Project structure created
  - ✅ Configuration files ready
  - ✅ Theme & design system implemented
  - ✅ MapView with Mapbox GL
  - ✅ User location tracking
  - ✅ API integration & polling
  - ✅ Zustand state management
  - ✅ Traffic heat map overlay
  - ✅ Parking markers
  - ✅ Swipeable bottom sheet
  - ✅ Traffic status display

---

## 🐛 **KNOWN ISSUES & BLOCKERS**

### **Active Issues**
- None yet

### **Resolved Issues**
- None yet

---

## 📝 **NOTES & DECISIONS**

### **Design Decisions**
1. **Full-screen map** - More immersive, better for navigation
2. **Bottom sheet** - Clean way to show data without obscuring map
3. **Heat map** - Intuitive traffic visualization
4. **Apple Maps style** - Professional, elegant, familiar

### **Technical Decisions**
1. **React Native** - Cross-platform, single codebase
2. **Mapbox GL** - Best map performance, Waze-like visuals
3. **Zustand** - Lightweight state management
4. **@gorhom/bottom-sheet** - Smooth native gestures

### **Optimizations**
1. Debounce API calls to stay within free tier
2. Cache map tiles for offline viewing
3. Use memoization for expensive calculations
4. Lazy load screens for faster startup

---

## 🎉 **SUCCESS CRITERIA**

### **MVP Complete When:**
- [x] User can view live traffic on map
- [ ] User can find parking near destination
- [ ] User can navigate to parking spot
- [ ] App updates in real-time (2s)
- [ ] All animations smooth (60fps)
- [ ] Works on Android emulator
- [ ] Light/dark theme switches automatically
- [ ] No crashes or major bugs

---

## 📞 **SUPPORT & RESOURCES**

### **Documentation**
- [React Native Docs](https://reactnative.dev/docs/getting-started)
- [Mapbox GL Docs](https://docs.mapbox.com/android/maps/guides/)
- [Bottom Sheet Docs](https://gorhom.github.io/react-native-bottom-sheet/)

### **API Reference**
- Backend: `http://localhost:8000/docs`
- Endpoint: `GET /api/v1/status/live`

---

**Last Updated:** 2025-10-23  
**Version:** 1.0  
**Status:** 🚧 In Progress  

---

**Let's build something amazing! 🚀**

