/**
 * UrbanFlowAI - Global State Store
 * Zustand store for app-wide state management
 */

import { create } from 'zustand';
import { Street, ParkingZone, api } from '../services/api';

interface AppState {
  // Traffic State
  streets: Street[];
  averageCongestion: number;
  trafficLoading: boolean;
  trafficError: string | null;

  // Parking State
  parkingZones: ParkingZone[];
  totalParkingSpots: number;
  totalFreeSpots: number;
  parkingLoading: boolean;
  parkingError: string | null;

  // General State
  lastUpdated: string | null;
  isPolling: boolean;

  // User Location (real-time)
  userLocation: {
    latitude: number | null;
    longitude: number | null;
  };

  // Actions
  fetchLiveData: () => Promise<void>;
  startPolling: () => void;
  stopPolling: () => void;
  clearErrors: () => void;
  setUserLocation: (coordinates: [number, number]) => void;
}

let pollingInterval: NodeJS.Timeout | null = null;

export const useAppStore = create<AppState>((set, get) => ({
  // Initial State
  streets: [],
  averageCongestion: 0,
  trafficLoading: false,
  trafficError: null,

  parkingZones: [],
  totalParkingSpots: 0,
  totalFreeSpots: 0,
  parkingLoading: false,
  parkingError: null,

  lastUpdated: null,
  isPolling: false,

  userLocation: {
    latitude: null,
    longitude: null,
  },

  // Fetch live data from API
  fetchLiveData: async () => {
    try {
      const response = await api.getLiveStatus();

      set({
        streets: response.streets || [],
        averageCongestion: response.average_congestion || 0,
        parkingZones: response.parking_zones || [],
        totalParkingSpots: response.total_parking_spots || 0,
        totalFreeSpots: response.total_free_spots || 0,
        lastUpdated: response.timestamp,
        trafficError: null,
        parkingError: null,
      });

      console.log('✅ Live data updated:', {
        streets: response.streets?.length,
        parking: response.parking_zones?.length,
      });
    } catch (error: any) {
      console.error('❌ Failed to fetch live data:', error.message);
      set({
        trafficError: 'Failed to load traffic data',
        parkingError: 'Failed to load parking data',
      });
    }
  },

  // Start polling every 2 seconds
  startPolling: () => {
    if (pollingInterval) {
      return; // Already polling
    }

    console.log('🔄 Starting real-time polling...');
    
    // Fetch immediately
    get().fetchLiveData();

    // Then poll every 2 seconds
    pollingInterval = setInterval(() => {
      get().fetchLiveData();
    }, 2000);

    set({ isPolling: true });
  },

  // Stop polling
  stopPolling: () => {
    if (pollingInterval) {
      console.log('⏸️  Stopping polling...');
      clearInterval(pollingInterval);
      pollingInterval = null;
      set({ isPolling: false });
    }
  },

  // Clear errors
  clearErrors: () => {
    set({
      trafficError: null,
      parkingError: null,
    });
  },

  // Set user location (real-time updates)
  setUserLocation: (coordinates: [number, number]) => {
    set({
      userLocation: {
        longitude: coordinates[0],
        latitude: coordinates[1],
      },
    });
  },
}));

export default useAppStore;

