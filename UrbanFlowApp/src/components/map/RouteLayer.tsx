/**
 * UrbanFlowAI - Route Layer
 * Draws navigation route on the map with traffic-aware styling
 */

import React from 'react';
import MapboxGL from '@rnmapbox/maps';

interface RouteLayerProps {
  coordinates: [number, number][]; // Array of [lon, lat]
  trafficImpact?: 'low' | 'medium' | 'high' | 'critical';
}

export const RouteLayer: React.FC<RouteLayerProps> = ({
  coordinates,
  trafficImpact = 'low',
}) => {
  // Get route color based on traffic impact
  const getRouteColor = (): string => {
    switch (trafficImpact) {
      case 'low':
        return '#10b981'; // Green
      case 'medium':
        return '#f59e0b'; // Yellow
      case 'high':
        return '#f97316'; // Orange
      case 'critical':
        return '#ef4444'; // Red
      default:
        return '#3b82f6'; // Blue
    }
  };

  if (!coordinates || coordinates.length < 2) {
    return null;
  }

  // Create GeoJSON for the route
  const routeGeoJSON: GeoJSON.Feature<GeoJSON.LineString> = {
    type: 'Feature',
    properties: {},
    geometry: {
      type: 'LineString',
      coordinates: coordinates,
    },
  };

  return (
    <>
      {/* Route Outline (wider, darker) */}
      <MapboxGL.ShapeSource id="routeOutlineSource" shape={routeGeoJSON}>
        <MapboxGL.LineLayer
          id="routeOutlineLayer"
          style={{
            lineColor: '#000000',
            lineWidth: 8,
            lineOpacity: 0.4,
            lineCap: 'round',
            lineJoin: 'round',
          }}
        />
      </MapboxGL.ShapeSource>

      {/* Route Main Line */}
      <MapboxGL.ShapeSource id="routeSource" shape={routeGeoJSON}>
        <MapboxGL.LineLayer
          id="routeLayer"
          style={{
            lineColor: getRouteColor(),
            lineWidth: 6,
            lineOpacity: 0.9,
            lineCap: 'round',
            lineJoin: 'round',
          }}
        />
      </MapboxGL.ShapeSource>

      {/* Route Glow Effect */}
      <MapboxGL.ShapeSource id="routeGlowSource" shape={routeGeoJSON}>
        <MapboxGL.LineLayer
          id="routeGlowLayer"
          style={{
            lineColor: getRouteColor(),
            lineWidth: 12,
            lineOpacity: 0.2,
            lineBlur: 4,
            lineCap: 'round',
            lineJoin: 'round',
          }}
        />
      </MapboxGL.ShapeSource>
    </>
  );
};

export default RouteLayer;

