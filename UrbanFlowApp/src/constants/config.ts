/**
 * UrbanFlowAI - Configuration
 * Central configuration for API, Mapbox, and app settings
 */

export const config = {
  // API Configuration
  api: {
    baseUrl: 'http://localhost:8000',
    endpoints: {
      liveStatus: '/api/v1/status/live',
      calculateRoute: '/api/v1/route/calculate',
      health: '/health',
    },
    pollInterval: 2000, // 2 seconds
    timeout: 10000, // 10 seconds
  },

  // Mapbox Configuration
  mapbox: {
    accessToken: 'pk.eyJ1IjoibmVndXJhdGVvZG9yciIsImEiOiJjbWgzaTJkcTAxNXkyZDNzYjlzbjg1andvIn0.J5GHR2HYPA3GxYuoS_xclA',
    styleUrl: 'mapbox://styles/mapbox/streets-v12',
    styleUrlDark: 'mapbox://styles/mapbox/dark-v11',
    defaultZoom: 14,
    minZoom: 10,
    maxZoom: 18,
    defaultCenter: {
      latitude: 40.7589,
      longitude: -73.9762,
    },
  },

  // App Configuration
  app: {
    name: 'UrbanFlowAI',
    version: '1.0.0',
    enableHaptics: true,
    enableAnimations: true,
    theme: 'auto', // 'light' | 'dark' | 'auto'
  },

  // Traffic Configuration
  traffic: {
    refreshInterval: 2000, // 2 seconds
    heatmapRadius: 30,
    heatmapIntensity: 1.5,
    particleCount: 15, // particles per street
    particleSpeed: 1.5, // pixels per frame
  },

  // Parking Configuration  
  parking: {
    searchRadius: 1000, // meters
    maxResults: 10,
    refreshInterval: 2000,
  },

  // Navigation Configuration
  navigation: {
    rerouteThreshold: 100, // meters off route
    routeLineWidth: 6,
    alternativeRouteOpacity: 0.5,
    voiceEnabled: false, // Voice guidance (future)
  },
};

export default config;

