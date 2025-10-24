/**
 * UrbanFlowAI - Navigation Screen
 * Turn-by-turn navigation with route overlay and ETA
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  useColorScheme,
  Alert,
  ScrollView,
} from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import UrbanFlowMapView from '../components/map/MapView';
import RouteLayer from '../components/map/RouteLayer';
import { colors, spacing, typography, borderRadius, shadows } from '../utils/theme';
import { api, RouteResponse } from '../services/api';
import { useAppStore } from '../store/store';
import { RootStackParamList } from '../navigation/AppNavigator';

type NavigationScreenRouteProp = RouteProp<RootStackParamList, 'Navigation'>;
type NavigationScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Navigation'>;

export const NavigationScreen: React.FC = () => {
  const navigation = useNavigation<NavigationScreenNavigationProp>();
  const navigationRoute = useRoute<NavigationScreenRouteProp>();
  const { destination } = navigationRoute.params;
  const colorScheme = useColorScheme();
  const theme = colorScheme === 'dark' ? colors.dark : colors.light;
  const { userLocation } = useAppStore();

  const [routeData, setRouteData] = useState<RouteResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [showInstructions, setShowInstructions] = useState(false);

  // Fetch route on mount
  useEffect(() => {
    const fetchRoute = async () => {
      if (!userLocation.latitude || !userLocation.longitude) {
        Alert.alert(
          'Location Required',
          'Cannot calculate route without your location. Please enable location access.'
        );
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const routeData = await api.calculateRoute({
          start_coords: [userLocation.longitude, userLocation.latitude],
          end_coords: [destination.longitude, destination.latitude],
        });

        setRouteData(routeData);
        console.log('✅ Route calculated:', routeData);
      } catch (error: any) {
        console.error('❌ Route calculation failed:', error);
        Alert.alert(
          'Route Error',
          'Failed to calculate route. Please try again.',
          [{ text: 'OK', onPress: () => navigation.goBack() }]
        );
      } finally {
        setLoading(false);
      }
    };

    fetchRoute();
  }, [userLocation, destination, navigation]);

  const formatDuration = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} min`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  };

  const formatDistance = (meters: number): string => {
    if (meters < 1000) return `${Math.round(meters)}m`;
    return `${(meters / 1000).toFixed(1)}km`;
  };

  const getTrafficImpactColor = (impact: string): string => {
    switch (impact) {
      case 'low':
        return '#10b981';
      case 'medium':
        return '#f59e0b';
      case 'high':
        return '#f97316';
      case 'critical':
        return '#ef4444';
      default:
        return '#3b82f6';
    }
  };

  const getTrafficImpactText = (impact: string): string => {
    switch (impact) {
      case 'low':
        return 'Light Traffic';
      case 'medium':
        return 'Moderate Traffic';
      case 'high':
        return 'Heavy Traffic';
      case 'critical':
        return 'Critical Traffic';
      default:
        return 'Unknown';
    }
  };

  const handleEndNavigation = () => {
    Alert.alert(
      'End Navigation',
      'Are you sure you want to stop navigation?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'End', style: 'destructive', onPress: () => navigation.goBack() },
      ]
    );
  };

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
        {/* Map with Route */}
        <View style={styles.mapContainer}>
          <UrbanFlowMapView>
            {/* Route Overlay */}
            {routeData && routeData.geometry && (
              <RouteLayer
                coordinates={routeData.geometry}
                trafficImpact={routeData.traffic_impact}
              />
            )}
          </UrbanFlowMapView>

          {/* Loading Overlay */}
          {loading && (
            <View style={styles.loadingOverlay}>
              <View style={[styles.loadingCard, { backgroundColor: theme.surface }, shadows.lg]}>
                <Text style={[styles.loadingText, { color: theme.textPrimary }]}>
                  🗺️ Calculating route...
                </Text>
              </View>
            </View>
          )}

          {/* Top Controls */}
          <View style={styles.topControls}>
            <TouchableOpacity
              style={[styles.controlButton, { backgroundColor: theme.surface }, shadows.md]}
              onPress={handleEndNavigation}
            >
              <Text style={[styles.controlIcon, { color: theme.danger }]}>✕</Text>
            </TouchableOpacity>
          </View>

          {/* ETA Card */}
          {routeData && !loading && (
            <View style={[styles.etaCard, { backgroundColor: theme.surface }, shadows.lg]}>
              <View style={styles.etaHeader}>
                <View style={styles.etaMain}>
                  <Text style={[styles.etaTime, { color: theme.textPrimary }]}>
                    {formatDuration(routeData.duration_seconds)}
                  </Text>
                  <Text style={[styles.etaLabel, { color: theme.textSecondary }]}>
                    ETA
                  </Text>
                </View>
                <View style={styles.etaDivider} />
                <View style={styles.etaDistance}>
                  <Text style={[styles.etaDistanceValue, { color: theme.textPrimary }]}>
                    {formatDistance(routeData.distance_meters)}
                  </Text>
                  <Text style={[styles.etaLabel, { color: theme.textSecondary }]}>
                    Distance
                  </Text>
                </View>
              </View>

              {/* Traffic Impact */}
              <View
                style={[
                  styles.trafficBadge,
                  { backgroundColor: getTrafficImpactColor(routeData.traffic_impact) },
                ]}
              >
                <Text style={styles.trafficText}>
                  🚦 {getTrafficImpactText(routeData.traffic_impact)}
                </Text>
              </View>
            </View>
          )}

          {/* Turn-by-Turn Instructions Toggle */}
          {routeData && routeData.instructions && routeData.instructions.length > 0 && (
            <TouchableOpacity
              style={[styles.instructionsToggle, { backgroundColor: theme.primary }, shadows.lg]}
              onPress={() => setShowInstructions(!showInstructions)}
            >
              <Text style={styles.instructionsToggleText}>
                {showInstructions ? '📍 Hide Steps' : '📍 Show Steps'}
              </Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Turn-by-Turn Instructions Panel */}
        {showInstructions && routeData && routeData.instructions && (
          <View style={[styles.instructionsPanel, { backgroundColor: theme.surface }, shadows.xl]}>
            <View style={styles.instructionsHeader}>
              <Text style={[styles.instructionsTitle, { color: theme.textPrimary }]}>
                Turn-by-Turn Directions
              </Text>
              <TouchableOpacity onPress={() => setShowInstructions(false)}>
                <Text style={[styles.closeButton, { color: theme.textSecondary }]}>✕</Text>
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.instructionsList} showsVerticalScrollIndicator={false}>
              {routeData.instructions.map((instruction, index) => (
                <View
                  key={index}
                  style={[
                    styles.instructionCard,
                    {
                      backgroundColor: index === currentStepIndex ? theme.primary + '20' : theme.cardBackground,
                      borderLeftColor: index === currentStepIndex ? theme.primary : theme.border,
                    },
                  ]}
                >
                  <View style={styles.instructionNumber}>
                    <Text style={[styles.instructionNumberText, { color: theme.textPrimary }]}>
                      {index + 1}
                    </Text>
                  </View>
                  <Text style={[styles.instructionText, { color: theme.textPrimary }]}>
                    {instruction.text}
                  </Text>
                </View>
              ))}
            </ScrollView>
          </View>
        )}
      </SafeAreaView>
    </GestureHandlerRootView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  mapContainer: {
    flex: 1,
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
  },
  loadingCard: {
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.lg,
    borderRadius: borderRadius.lg,
  },
  loadingText: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semibold,
  },
  topControls: {
    position: 'absolute',
    top: spacing.md,
    left: spacing.md,
    right: spacing.md,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  controlButton: {
    width: 48,
    height: 48,
    borderRadius: borderRadius.full,
    justifyContent: 'center',
    alignItems: 'center',
  },
  controlIcon: {
    fontSize: 24,
    fontWeight: '600',
  },
  etaCard: {
    position: 'absolute',
    top: 80,
    left: spacing.md,
    right: spacing.md,
    padding: spacing.md,
    borderRadius: borderRadius.lg,
  },
  etaHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  etaMain: {
    flex: 1,
  },
  etaTime: {
    fontSize: 32,
    fontWeight: typography.fontWeight.bold,
    marginBottom: spacing.xs,
  },
  etaLabel: {
    fontSize: typography.fontSize.sm,
  },
  etaDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#E5E5EA',
    marginHorizontal: spacing.md,
  },
  etaDistance: {
    alignItems: 'flex-end',
  },
  etaDistanceValue: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    marginBottom: spacing.xs,
  },
  trafficBadge: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.full,
    alignSelf: 'flex-start',
  },
  trafficText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold,
    color: '#FFFFFF',
  },
  instructionsToggle: {
    position: 'absolute',
    bottom: spacing.xl,
    alignSelf: 'center',
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.full,
  },
  instructionsToggleText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: '#FFFFFF',
  },
  instructionsPanel: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    maxHeight: '50%',
    borderTopLeftRadius: borderRadius.xl,
    borderTopRightRadius: borderRadius.xl,
    paddingTop: spacing.md,
  },
  instructionsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingBottom: spacing.md,
  },
  instructionsTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
  },
  closeButton: {
    fontSize: 24,
    fontWeight: '600',
  },
  instructionsList: {
    paddingHorizontal: spacing.md,
  },
  instructionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderRadius: borderRadius.md,
    borderLeftWidth: 4,
  },
  instructionNumber: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(59, 130, 246, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  instructionNumberText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
  },
  instructionText: {
    flex: 1,
    fontSize: typography.fontSize.base,
  },
});

export default NavigationScreen;

