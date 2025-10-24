/**
 * UrbanFlowAI - API Service
 * HTTP client for backend communication
 */

import axios, { AxiosInstance } from 'axios';
import config from '../constants/config';

// Types
export interface Street {
  street_id: string;
  street_name: string;
  congestion_score: number;
  congestion_level: 'low' | 'medium' | 'high' | 'critical';
  coordinates: number[][];
  max_speed?: number;
}

export interface ParkingSpot {
  spot_id: string;
  status: 'occupied' | 'free';
}

export interface ParkingZone {
  zone_id: string;
  zone_name: string;
  total_spots: number;
  free_spots: number;
  occupancy_rate: number;
  latitude: number;
  longitude: number;
  spots: ParkingSpot[];
}

export interface LiveStatusResponse {
  timestamp: string;
  streets: Street[];
  average_congestion: number;
  parking_zones: ParkingZone[];
  total_parking_spots: number;
  total_free_spots: number;
  emergency_vehicles: any[];
  active_emergencies: number;
}

export interface RouteRequest {
  start_coords: [number, number]; // [lon, lat]
  end_coords: [number, number];   // [lon, lat]
}

export interface RouteInstruction {
  text: string;
  point: [number, number]; // [lon, lat]
}

export interface RouteResponse {
  route_id: string;
  duration_seconds: number;
  distance_meters: number;
  geometry: number[][]; // [[lon, lat], ...]
  instructions: RouteInstruction[];
  traffic_impact: 'low' | 'medium' | 'high' | 'critical';
}

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: config.api.baseUrl,
      timeout: config.api.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      request => {
        console.log('API Request:', request.method?.toUpperCase(), request.url);
        return request;
      },
      error => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      response => {
        console.log('API Response:', response.status, response.config.url);
        return response;
      },
      error => {
        console.error('API Response Error:', error.response?.status, error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get live traffic and parking status
   */
  async getLiveStatus(): Promise<LiveStatusResponse> {
    try {
      const response = await this.client.get<LiveStatusResponse>(
        config.api.endpoints.liveStatus
      );
      return response.data;
    } catch (error) {
      console.error('Failed to fetch live status:', error);
      throw error;
    }
  }

  /**
   * Calculate route from origin to destination
   */
  async calculateRoute(request: RouteRequest): Promise<RouteResponse> {
    try {
      const response = await this.client.post<RouteResponse>(
        config.api.endpoints.calculateRoute,
        request
      );
      return response.data;
    } catch (error) {
      console.error('Failed to calculate route:', error);
      throw error;
    }
  }

  /**
   * Check API health
   */
  async checkHealth(): Promise<{ status: string }> {
    try {
      const response = await this.client.get<{ status: string }>(
        config.api.endpoints.health
      );
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const api = new ApiService();
export default api;

