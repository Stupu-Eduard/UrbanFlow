/**
 * UrbanFlowAI - MapView Component
 * Full-screen Mapbox GL map with user location and traffic overlay
 */

import React, { useRef, useEffect, useState } from 'react';
import { StyleSheet } from 'react-native';
import MapboxGL from '@rnmapbox/maps';
import config from '../../constants/config';
import { useColorScheme } from 'react-native';
import { requestLocationPermission } from '../../utils/permissions';

// Configure Mapbox
MapboxGL.setAccessToken(config.mapbox.accessToken);
MapboxGL.setTelemetryEnabled(false); // Disable telemetry to save on free tier

interface MapViewProps {
  onMapReady?: () => void;
  onRegionChanged?: (coordinates: [number, number]) => void;
  onLocationUpdate?: (coordinates: [number, number]) => void;
  children?: React.ReactNode;
}

export const UrbanFlowMapView: React.FC<MapViewProps> = ({
  onMapReady,
  onRegionChanged,
  onLocationUpdate,
  children,
}) => {
  const mapRef = useRef<MapboxGL.MapView>(null);
  const cameraRef = useRef<MapboxGL.Camera>(null);
  const colorScheme = useColorScheme();
  const [locationPermissionGranted, setLocationPermissionGranted] = useState(false);
  const [isFollowingUser, setIsFollowingUser] = useState(true);

  // Auto-switch map style based on time of day
  const getMapStyle = () => {
    const hour = new Date().getHours();
    const isDarkMode = hour < 6 || hour > 19; // Dark mode 7PM-6AM
    
    if (colorScheme === 'dark' || isDarkMode) {
      return config.mapbox.styleUrlDark;
    }
    return config.mapbox.styleUrl;
  };

  // Request location permission on mount
  useEffect(() => {
    const requestPermission = async () => {
      const granted = await requestLocationPermission();
      setLocationPermissionGranted(granted);
      if (granted) {
        console.log('✅ Location tracking enabled - real-time updates active');
      }
    };
    requestPermission();
  }, []);

  // Initialize map
  useEffect(() => {
    if (onMapReady) {
      setTimeout(onMapReady, 1000); // Wait for map to fully load
    }
  }, [onMapReady]);

  // Handle user location updates
  const handleUserLocationUpdate = (location: MapboxGL.Location) => {
    const coordinates: [number, number] = [
      location.coords.longitude,
      location.coords.latitude,
    ];
    
    console.log('📍 Location update:', coordinates);
    
    if (onLocationUpdate) {
      onLocationUpdate(coordinates);
    }

    // Follow user location if enabled
    if (isFollowingUser && cameraRef.current) {
      cameraRef.current.setCamera({
        centerCoordinate: coordinates,
        zoomLevel: 15,
        animationDuration: 1000,
      });
    }
  };

  const handleRegionDidChange = async () => {
    if (mapRef.current) {
      const center = await mapRef.current.getCenter();
      if (onRegionChanged && center) {
        onRegionChanged(center as [number, number]);
      }
    }
  };

  return (
    <MapboxGL.MapView
      ref={mapRef}
      style={styles.map}
      styleURL={getMapStyle()}
      onDidFinishLoadingMap={onMapReady}
      onRegionDidChange={handleRegionDidChange}
      compassEnabled={true}
      compassViewPosition={3} // Bottom right
      compassViewMargins={{ x: 16, y: 100 }}
      logoEnabled={false}
      attributionEnabled={false}
      scaleBarEnabled={false}
    >
      <MapboxGL.Camera
        ref={cameraRef}
        zoomLevel={config.mapbox.defaultZoom}
        centerCoordinate={[
          config.mapbox.defaultCenter.longitude,
          config.mapbox.defaultCenter.latitude,
        ]}
        animationMode="flyTo"
        animationDuration={2000}
        followUserLocation={isFollowingUser && locationPermissionGranted}
        followUserMode="normal"
      />

      {/* User Location - Real-time tracking (only when permission granted) */}
      {locationPermissionGranted && (
        <MapboxGL.UserLocation
          visible={true}
          showsUserHeadingIndicator={true}
          androidRenderMode="gps"
          minDisplacement={5} // Update every 5 meters
          onUpdate={handleUserLocationUpdate}
        />
      )}

      {/* Children (layers, markers, etc.) */}
      {children}
    </MapboxGL.MapView>
  );
};

const styles = StyleSheet.create({
  map: {
    flex: 1,
  },
});

export default UrbanFlowMapView;

