/**
 * UrbanFlowAI - Parking Grid
 * Visual grid showing individual parking spot statuses
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, useColorScheme } from 'react-native';
import { ParkingSpot } from '../../services/api';
import { colors, spacing, borderRadius } from '../../utils/theme';

interface ParkingGridProps {
  spots: ParkingSpot[];
  columns?: number;
  onSpotPress?: (spot: ParkingSpot) => void;
}

export const ParkingGrid: React.FC<ParkingGridProps> = ({
  spots,
  columns = 10,
  onSpotPress,
}) => {
  const colorScheme = useColorScheme();
  const theme = colorScheme === 'dark' ? colors.dark : colors.light;

  const getSpotColor = (status: string): string => {
    return status === 'free' ? '#10b981' : '#ef4444';
  };

  const getSpotNumber = (spotId: string): string => {
    // Extract number from spot_id (e.g., "SPOT_A1" → "1")
    const match = spotId.match(/\d+$/);
    return match ? match[0] : '?';
  };

  // Group spots into rows
  const rows: ParkingSpot[][] = [];
  for (let i = 0; i < spots.length; i += columns) {
    rows.push(spots.slice(i, i + columns));
  }

  return (
    <View style={styles.container}>
      {rows.map((row, rowIndex) => (
        <View key={rowIndex} style={styles.row}>
          {row.map((spot) => (
            <TouchableOpacity
              key={spot.spot_id}
              style={[
                styles.spot,
                {
                  backgroundColor: getSpotColor(spot.status),
                  borderColor: theme.border,
                },
              ]}
              onPress={() => onSpotPress?.(spot)}
              activeOpacity={0.7}
            >
              <Text style={styles.spotNumber}>
                {getSpotNumber(spot.spot_id)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      ))}

      {/* Legend */}
      <View style={styles.legend}>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#10b981' }]} />
          <Text style={[styles.legendText, { color: theme.textSecondary }]}>
            Available
          </Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#ef4444' }]} />
          <Text style={[styles.legendText, { color: theme.textSecondary }]}>
            Occupied
          </Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
  },
  row: {
    flexDirection: 'row',
    marginBottom: spacing.xs,
    gap: spacing.xs,
  },
  spot: {
    width: 32,
    height: 32,
    borderRadius: borderRadius.sm,
    borderWidth: 2,
    justifyContent: 'center',
    alignItems: 'center',
  },
  spotNumber: {
    fontSize: 10,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  legend: {
    flexDirection: 'row',
    gap: spacing.lg,
    marginTop: spacing.md,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  legendDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  legendText: {
    fontSize: 12,
  },
});

export default ParkingGrid;

