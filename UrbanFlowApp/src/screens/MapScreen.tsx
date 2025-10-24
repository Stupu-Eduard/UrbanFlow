/**
 * UrbanFlowAI - Map Screen
 * Main screen with full-screen map, traffic overlay, and bottom sheet
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  useColorScheme,
  Modal,
} from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import UrbanFlowMapView from '../components/map/MapView';
import HeatMapLayer from '../components/map/HeatMapLayer';
import ParkingMarker from '../components/map/ParkingMarker';
import BottomSheet from '../components/bottomSheet/BottomSheet';
import TrafficStatus from '../components/bottomSheet/TrafficStatus';
import ParkingList from '../components/bottomSheet/ParkingList';
import ParkingDetailScreen from './ParkingDetailScreen';
import { colors, spacing, typography, shadows } from '../utils/theme';
import { useAppStore } from '../store/store';
import { ParkingZone } from '../services/api';
import { RootStackParamList } from '../navigation/AppNavigator';

type BottomSheetView = 'traffic' | 'parking';
type NavigationProp = StackNavigationProp<RootStackParamList, 'Map'>;

export const MapScreen: React.FC = () => {
  const navigation = useNavigation<NavigationProp>();
  const [mapReady, setMapReady] = useState(false);
  const [bottomSheetView, setBottomSheetView] = useState<BottomSheetView>('traffic');
  const [selectedZone, setSelectedZone] = useState<ParkingZone | null>(null);
  const [showParkingDetail, setShowParkingDetail] = useState(false);
  const colorScheme = useColorScheme();
  const theme = colorScheme === 'dark' ? colors.dark : colors.light;

  // Get state from store
  const {
    streets,
    parkingZones,
    averageCongestion,
    totalParkingSpots,
    totalFreeSpots,
    lastUpdated,
    userLocation,
    startPolling,
    stopPolling,
    setUserLocation,
  } = useAppStore();

  useEffect(() => {
    console.log('🚀 MapScreen mounted');
    
    // Start polling for real-time data
    startPolling();

    // Cleanup on unmount
    return () => {
      console.log('🛑 MapScreen unmounting, stopping polling');
      stopPolling();
    };
  }, [startPolling, stopPolling]);

  const handleMapReady = () => {
    setMapReady(true);
    console.log('✅ Map is ready!');
  };

  const handleLocationUpdate = (coordinates: [number, number]) => {
    setUserLocation(coordinates);
    console.log('📍 User location updated:', coordinates);
  };

  const handleParkingPress = (zone: ParkingZone) => {
    console.log('🅿️ Parking zone pressed:', zone.zone_name);
    setSelectedZone(zone);
    setShowParkingDetail(true);
  };

  const handleNavigate = (zone: ParkingZone) => {
    console.log('🧭 Navigate to:', zone.zone_name);
    navigation.navigate('Navigation', {
      destination: {
        latitude: zone.latitude,
        longitude: zone.longitude,
        name: zone.zone_name,
      },
    });
  };

  const handleCloseParkingDetail = () => {
    setShowParkingDetail(false);
    setSelectedZone(null);
  };

  const toggleBottomSheetView = () => {
    setBottomSheetView(prev => prev === 'traffic' ? 'parking' : 'traffic');
  };

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
        {/* Header */}
        <View style={[styles.header, { backgroundColor: theme.surface }, shadows.sm]}>
          <TouchableOpacity style={styles.menuButton}>
            <Text style={[styles.menuIcon, { color: theme.textPrimary }]}>☰</Text>
          </TouchableOpacity>
          
          <View style={styles.headerCenter}>
            <Text style={[styles.headerTitle, { color: theme.textPrimary }]}>
              UrbanFlow
            </Text>
            <View style={styles.liveIndicator}>
              <View style={styles.liveDot} />
              <Text style={[styles.liveText, { color: theme.textSecondary }]}>
                LIVE
              </Text>
            </View>
          </View>

          <View style={styles.headerRight}>
            <TouchableOpacity style={styles.iconButton}>
              <Text style={[styles.icon, { color: theme.textPrimary }]}>🔔</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.iconButton}>
              <Text style={[styles.icon, { color: theme.textPrimary }]}>⚙️</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Map */}
        <View style={styles.mapContainer}>
          <UrbanFlowMapView 
            onMapReady={handleMapReady}
            onLocationUpdate={handleLocationUpdate}
          >
            {/* Traffic Heat Map Overlay */}
            {mapReady && streets.length > 0 && (
              <HeatMapLayer streets={streets} />
            )}

            {/* Parking Markers */}
            {mapReady && parkingZones.map((zone) => (
              <ParkingMarker
                key={zone.zone_id}
                zone={zone}
                onPress={handleParkingPress}
              />
            ))}
          </UrbanFlowMapView>

          {/* Search Bar */}
          <View style={[styles.searchContainer, shadows.md]}>
            <TouchableOpacity 
              style={[styles.searchBar, { backgroundColor: theme.cardBackground }]}
              onPress={() => console.log('🔍 Search pressed')}
            >
              <Text style={[styles.searchIcon, { color: theme.textSecondary }]}>
                🔍
              </Text>
              <Text style={[styles.searchPlaceholder, { color: theme.textSecondary }]}>
                Where to?
              </Text>
            </TouchableOpacity>
          </View>

          {/* Current Location Button */}
          <TouchableOpacity 
            style={[styles.locationButton, { backgroundColor: theme.cardBackground }, shadows.md]}
            onPress={() => console.log('📍 Center on user location')}
          >
            <Text style={styles.locationIcon}>📍</Text>
          </TouchableOpacity>

          {/* Loading Indicator */}
          {!mapReady && (
            <View style={[styles.loadingOverlay, { backgroundColor: theme.overlay }]}>
              <Text style={[styles.loadingText, { color: theme.textPrimary }]}>
                Loading map...
              </Text>
            </View>
          )}

          {/* Data Loading Indicator */}
          {mapReady && streets.length === 0 && (
            <View style={[styles.dataLoading, { backgroundColor: theme.surface }, shadows.md]}>
              <Text style={[styles.dataLoadingText, { color: theme.textSecondary }]}>
                🔄 Fetching traffic data...
              </Text>
            </View>
          )}
        </View>

        {/* Bottom Sheet with Traffic Status or Parking List */}
        <BottomSheet snapPoints={bottomSheetView === 'traffic' ? ['15%', '40%', '90%'] : ['50%', '90%']}>
          {bottomSheetView === 'traffic' ? (
            <TrafficStatus
              averageCongestion={averageCongestion}
              totalFreeSpots={totalFreeSpots}
              totalSpots={totalParkingSpots}
              lastUpdated={lastUpdated || undefined}
            />
          ) : (
            <ParkingList
              parkingZones={parkingZones}
              onNavigate={handleNavigate}
              onParkingPress={handleParkingPress}
              userLocation={userLocation.latitude && userLocation.longitude 
                ? { latitude: userLocation.latitude, longitude: userLocation.longitude }
                : undefined
              }
            />
          )}
        </BottomSheet>

        {/* View Toggle Button */}
        <TouchableOpacity
          style={[styles.viewToggleButton, { backgroundColor: theme.primary }, shadows.lg]}
          onPress={toggleBottomSheetView}
        >
          <Text style={styles.viewToggleText}>
            {bottomSheetView === 'traffic' ? '🅿️ Parking' : '📊 Traffic'}
          </Text>
        </TouchableOpacity>

        {/* Parking Detail Modal */}
        <Modal
          visible={showParkingDetail}
          animationType="slide"
          presentationStyle="pageSheet"
          onRequestClose={handleCloseParkingDetail}
        >
          {selectedZone && (
            <ParkingDetailScreen
              zone={selectedZone}
              onBack={handleCloseParkingDetail}
              onNavigate={handleNavigate}
            />
          )}
        </Modal>
      </SafeAreaView>
    </GestureHandlerRootView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    height: 60,
  },
  menuButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  menuIcon: {
    fontSize: 24,
  },
  headerCenter: {
    flex: 1,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
  },
  liveIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
  },
  liveDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#10b981',
    marginRight: 4,
  },
  liveText: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.semibold,
  },
  headerRight: {
    flexDirection: 'row',
    gap: spacing.xs,
  },
  iconButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  icon: {
    fontSize: 20,
  },
  mapContainer: {
    flex: 1,
  },
  searchContainer: {
    position: 'absolute',
    top: spacing.md,
    left: spacing.md,
    right: spacing.md,
    zIndex: 10,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    borderRadius: 28,
  },
  searchIcon: {
    fontSize: 20,
    marginRight: spacing.sm,
  },
  searchPlaceholder: {
    fontSize: typography.fontSize.base,
  },
  locationButton: {
    position: 'absolute',
    bottom: 180,
    left: spacing.md,
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
  },
  locationIcon: {
    fontSize: 24,
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 100,
  },
  loadingText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.medium,
  },
  dataLoading: {
    position: 'absolute',
    top: 100,
    alignSelf: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: 20,
  },
  dataLoadingText: {
    fontSize: typography.fontSize.sm,
  },
  viewToggleButton: {
    position: 'absolute',
    bottom: 200,
    right: spacing.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.full,
    zIndex: 10,
  },
  viewToggleText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold,
    color: '#FFFFFF',
  },
});

export default MapScreen;
