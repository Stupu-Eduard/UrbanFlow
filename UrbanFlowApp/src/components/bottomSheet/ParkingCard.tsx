/**
 * UrbanFlowAI - Parking Card
 * Individual parking zone card with details and navigate button
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, useColorScheme } from 'react-native';
import { ParkingZone } from '../../services/api';
import { colors, spacing, typography, borderRadius, shadows, getParkingColor } from '../../utils/theme';

interface ParkingCardProps {
  zone: ParkingZone;
  onNavigate: (zone: ParkingZone) => void;
  onPress: (zone: ParkingZone) => void;
  distance?: number; // meters
}

export const ParkingCard: React.FC<ParkingCardProps> = ({
  zone,
  onNavigate,
  onPress,
  distance,
}) => {
  const colorScheme = useColorScheme();
  const theme = colorScheme === 'dark' ? colors.dark : colors.light;

  const occupancyRate = zone.occupancy_rate;
  const occupancyColor = getParkingColor(occupancyRate);
  const percentage = Math.round(occupancyRate * 100);

  const formatDistance = (meters?: number): string => {
    if (!meters) return 'Unknown';
    if (meters < 1000) return `${Math.round(meters)}m away`;
    return `${(meters / 1000).toFixed(1)}km away`;
  };

  const getWalkingTime = (meters?: number): string => {
    if (!meters) return '';
    const minutes = Math.round(meters / 80); // ~80m per minute walking
    return `${minutes} min walk`;
  };

  const getStatusEmoji = (): string => {
    if (occupancyRate < 0.5) return '🟢';
    if (occupancyRate < 0.8) return '🟡';
    return '🔴';
  };

  return (
    <TouchableOpacity
      style={[
        styles.card,
        {
          backgroundColor: theme.cardBackground,
          borderColor: occupancyColor,
        },
        shadows.md,
      ]}
      onPress={() => onPress(zone)}
      activeOpacity={0.7}
    >
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.icon}>🅿️</Text>
          <View style={styles.headerText}>
            <Text style={[styles.zoneName, { color: theme.textPrimary }]}>
              {zone.zone_name}
            </Text>
            <Text style={[styles.zoneId, { color: theme.textSecondary }]}>
              {zone.zone_id}
            </Text>
          </View>
        </View>

        {/* Occupancy Badge */}
        <View style={[styles.badge, { backgroundColor: occupancyColor }]}>
          <Text style={styles.badgeText}>{getStatusEmoji()} {percentage}%</Text>
        </View>
      </View>

      {/* Occupancy Info */}
      <View style={styles.occupancyRow}>
        <Text style={[styles.occupancyText, { color: theme.textPrimary }]}>
          <Text style={[styles.occupancyNumber, { color: occupancyColor }]}>
            {zone.free_spots}
          </Text>
          {' '}of {zone.total_spots} spots free
        </Text>
      </View>

      {/* Details Grid */}
      <View style={styles.detailsGrid}>
        <View style={styles.detailItem}>
          <Text style={styles.detailIcon}>📍</Text>
          <Text style={[styles.detailText, { color: theme.textSecondary }]}>
            {formatDistance(distance)}
          </Text>
        </View>

        {distance && (
          <View style={styles.detailItem}>
            <Text style={styles.detailIcon}>🚶</Text>
            <Text style={[styles.detailText, { color: theme.textSecondary }]}>
              {getWalkingTime(distance)}
            </Text>
          </View>
        )}

        <View style={styles.detailItem}>
          <Text style={styles.detailIcon}>💳</Text>
          <Text style={[styles.detailText, { color: theme.textSecondary }]}>
            $2/hr
          </Text>
        </View>

        <View style={styles.detailItem}>
          <Text style={styles.detailIcon}>🕐</Text>
          <Text style={[styles.detailText, { color: theme.textSecondary }]}>
            24/7
          </Text>
        </View>
      </View>

      {/* Divider */}
      <View style={[styles.divider, { backgroundColor: theme.border }]} />

      {/* Navigate Button */}
      <TouchableOpacity
        style={[styles.navigateButton, { backgroundColor: theme.primary }]}
        onPress={() => onNavigate(zone)}
        activeOpacity={0.8}
      >
        <Text style={styles.navigateText}>Navigate →</Text>
      </TouchableOpacity>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    marginBottom: spacing.md,
    padding: spacing.md,
    borderRadius: borderRadius.lg,
    borderWidth: 2,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.sm,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  icon: {
    fontSize: 24,
    marginRight: spacing.sm,
  },
  headerText: {
    flex: 1,
  },
  zoneName: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold,
    marginBottom: 2,
  },
  zoneId: {
    fontSize: typography.fontSize.xs,
  },
  badge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.full,
  },
  badgeText: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.bold,
    color: '#FFFFFF',
  },
  occupancyRow: {
    marginBottom: spacing.md,
  },
  occupancyText: {
    fontSize: typography.fontSize.sm,
  },
  occupancyNumber: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
  },
  detailsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    minWidth: '45%',
  },
  detailIcon: {
    fontSize: 16,
    marginRight: 4,
  },
  detailText: {
    fontSize: typography.fontSize.sm,
  },
  divider: {
    height: 1,
    marginBottom: spacing.md,
  },
  navigateButton: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.lg,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
  },
  navigateText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold,
    color: '#FFFFFF',
  },
});

export default ParkingCard;

