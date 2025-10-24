/**
 * UrbanFlowAI - Heat Map Layer
 * Traffic congestion heat map overlay using Mapbox
 */

import React from 'react';
import MapboxGL from '@rnmapbox/maps';
import { Street } from '../../services/api';
import { getCongestionColor } from '../../utils/theme';

interface HeatMapLayerProps {
  streets: Street[];
}

export const HeatMapLayer: React.FC<HeatMapLayerProps> = ({ streets }) => {
  if (!streets || streets.length === 0) {
    return null;
  }

  // Convert streets to GeoJSON features
  const features = streets.map((street) => ({
    type: 'Feature' as const,
    properties: {
      congestion: street.congestion_score,
      name: street.street_name,
      level: street.congestion_level,
    },
    geometry: {
      type: 'LineString' as const,
      coordinates: street.coordinates.map(coord => [coord[0], coord[1]]),
    },
  }));

  const geojson = {
    type: 'FeatureCollection' as const,
    features,
  };

  return (
    <>
      {/* Street Lines with Color-Coded Congestion */}
      <MapboxGL.ShapeSource id="traffic-source" shape={geojson}>
        <MapboxGL.LineLayer
          id="traffic-lines"
          style={{
            lineColor: [
              'step',
              ['get', 'congestion'],
              '#10b981', // Green (0-40%)
              0.4, '#f59e0b', // Yellow (40-60%)
              0.6, '#f97316', // Orange (60-80%)
              0.8, '#ef4444', // Red (80-100%)
            ],
            lineWidth: [
              'interpolate',
              ['linear'],
              ['zoom'],
              10, 3,
              14, 6,
              18, 10,
            ],
            lineOpacity: 0.8,
            lineCap: 'round',
            lineJoin: 'round',
          }}
        />

        {/* Glow effect for better visibility */}
        <MapboxGL.LineLayer
          id="traffic-lines-glow"
          belowLayerID="traffic-lines"
          style={{
            lineColor: [
              'step',
              ['get', 'congestion'],
              '#10b981',
              0.4, '#f59e0b',
              0.6, '#f97316',
              0.8, '#ef4444',
            ],
            lineWidth: [
              'interpolate',
              ['linear'],
              ['zoom'],
              10, 6,
              14, 12,
              18, 20,
            ],
            lineOpacity: 0.3,
            lineBlur: 4,
            lineCap: 'round',
            lineJoin: 'round',
          }}
        />
      </MapboxGL.ShapeSource>

      {/* Heat map overlay for congestion density */}
      <MapboxGL.HeatmapLayer
        id="traffic-heatmap"
        sourceID="traffic-source"
        style={{
          heatmapWeight: [
            'interpolate',
            ['linear'],
            ['get', 'congestion'],
            0, 0,
            1, 1,
          ],
          heatmapIntensity: [
            'interpolate',
            ['linear'],
            ['zoom'],
            0, 1,
            14, 1.5,
          ],
          heatmapColor: [
            'interpolate',
            ['linear'],
            ['heatmap-density'],
            0, 'rgba(16, 185, 129, 0)', // Transparent green
            0.2, 'rgba(16, 185, 129, 0.4)', // Green
            0.4, 'rgba(245, 158, 11, 0.5)', // Yellow
            0.6, 'rgba(249, 115, 22, 0.6)', // Orange
            0.8, 'rgba(239, 68, 68, 0.7)', // Red
            1, 'rgba(239, 68, 68, 0.9)', // Dark red
          ],
          heatmapRadius: [
            'interpolate',
            ['linear'],
            ['zoom'],
            10, 20,
            14, 30,
            18, 50,
          ],
          heatmapOpacity: 0.6,
        }}
      />
    </>
  );
};

export default HeatMapLayer;

