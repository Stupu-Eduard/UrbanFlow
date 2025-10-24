/**
 * UrbanFlowAI - Parking List
 * Scrollable list of parking zones (half-open bottom sheet)
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView, useColorScheme } from 'react-native';
import { ParkingZone } from '../../services/api';
import ParkingCard from './ParkingCard';
import { colors, spacing, typography } from '../../utils/theme';

interface ParkingListProps {
  parkingZones: ParkingZone[];
  onNavigate: (zone: ParkingZone) => void;
  onParkingPress: (zone: ParkingZone) => void;
  userLocation?: { latitude: number; longitude: number };
}

export const ParkingList: React.FC<ParkingListProps> = ({
  parkingZones,
  onNavigate,
  onParkingPress,
  userLocation,
}) => {
  const colorScheme = useColorScheme();
  const theme = colorScheme === 'dark' ? colors.dark : colors.light;

  // Calculate distance from user to parking zone
  const calculateDistance = (zone: ParkingZone): number => {
    if (!userLocation) return 0;

    const R = 6371e3; // Earth radius in meters
    const φ1 = (userLocation.latitude * Math.PI) / 180;
    const φ2 = (zone.latitude * Math.PI) / 180;
    const Δφ = ((zone.latitude - userLocation.latitude) * Math.PI) / 180;
    const Δλ = ((zone.longitude - userLocation.longitude) * Math.PI) / 180;

    const a =
      Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
      Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c; // Distance in meters
  };

  // Sort parking zones by distance (closest first)
  const sortedZones = [...parkingZones].sort((a, b) => {
    const distA = calculateDistance(a);
    const distB = calculateDistance(b);
    return distA - distB;
  });

  if (parkingZones.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={[styles.emptyIcon, { color: theme.textSecondary }]}>
          🅿️
        </Text>
        <Text style={[styles.emptyText, { color: theme.textSecondary }]}>
          No parking zones available
        </Text>
        <Text style={[styles.emptySubtext, { color: theme.textSecondary }]}>
          Waiting for data...
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={[styles.title, { color: theme.textPrimary }]}>
          🅿️ Nearby Parking ({parkingZones.length})
        </Text>
        <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
          Sorted by distance
        </Text>
      </View>

      {/* Parking Cards */}
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {sortedZones.map((zone) => (
          <ParkingCard
            key={zone.zone_id}
            zone={zone}
            onNavigate={onNavigate}
            onPress={onParkingPress}
            distance={calculateDistance(zone)}
          />
        ))}

        {/* Bottom Padding */}
        <View style={styles.bottomPadding} />
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
  },
  title: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.fontSize.sm,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: spacing.md,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: spacing.md,
    opacity: 0.5,
  },
  emptyText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.medium,
    marginBottom: spacing.xs,
  },
  emptySubtext: {
    fontSize: typography.fontSize.sm,
  },
  bottomPadding: {
    height: 100, // Extra space at bottom for comfortable scrolling
  },
});

export default ParkingList;

