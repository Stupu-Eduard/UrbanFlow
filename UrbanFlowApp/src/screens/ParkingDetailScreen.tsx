/**
 * UrbanFlowAI - Parking Detail Screen
 * Full detail view of a parking zone with spot grid
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  useColorScheme,
} from 'react-native';
import { ParkingZone, ParkingSpot } from '../services/api';
import ParkingGrid from '../components/common/ParkingGrid';
import { colors, spacing, typography, borderRadius, shadows, getParkingColor } from '../utils/theme';

interface ParkingDetailScreenProps {
  zone: ParkingZone;
  onBack: () => void;
  onNavigate: (zone: ParkingZone) => void;
}

export const ParkingDetailScreen: React.FC<ParkingDetailScreenProps> = ({
  zone,
  onBack,
  onNavigate,
}) => {
  const colorScheme = useColorScheme();
  const theme = colorScheme === 'dark' ? colors.dark : colors.light;

  const occupancyRate = zone.occupancy_rate;
  const occupancyColor = getParkingColor(occupancyRate);
  const percentage = Math.round(occupancyRate * 100);

  const handleSpotPress = (spot: ParkingSpot) => {
    console.log('Spot pressed:', spot.spot_id, spot.status);
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
      {/* Header */}
      <View style={[styles.header, { backgroundColor: theme.surface }, shadows.sm]}>
        <TouchableOpacity style={styles.backButton} onPress={onBack}>
          <Text style={[styles.backIcon, { color: theme.primary }]}>←</Text>
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: theme.textPrimary }]}>
          Parking Details
        </Text>
        <View style={styles.headerRight} />
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Zone Name */}
        <View style={styles.section}>
          <View style={styles.titleRow}>
            <Text style={styles.icon}>🅿️</Text>
            <Text style={[styles.zoneName, { color: theme.textPrimary }]}>
              {zone.zone_name}
            </Text>
          </View>
        </View>

        {/* Occupancy Card */}
        <View style={[styles.card, { backgroundColor: theme.surface }, shadows.md]}>
          <Text style={[styles.cardTitle, { color: theme.textPrimary }]}>
            📊 Occupancy
          </Text>

          {/* Progress Bar */}
          <View style={styles.progressContainer}>
            <View style={[styles.progressBackground, { backgroundColor: theme.border }]}>
              <View
                style={[
                  styles.progressFill,
                  {
                    width: `${percentage}%`,
                    backgroundColor: occupancyColor,
                  },
                ]}
              />
            </View>
            <Text style={[styles.percentage, { color: theme.textPrimary }]}>
              {percentage}%
            </Text>
          </View>

          {/* Stats */}
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={[styles.statValue, { color: occupancyColor }]}>
                {zone.free_spots}
              </Text>
              <Text style={[styles.statLabel, { color: theme.textSecondary }]}>
                Available
              </Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={[styles.statValue, { color: theme.textPrimary }]}>
                {zone.total_spots - zone.free_spots}
              </Text>
              <Text style={[styles.statLabel, { color: theme.textSecondary }]}>
                Occupied
              </Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={[styles.statValue, { color: theme.textPrimary }]}>
                {zone.total_spots}
              </Text>
              <Text style={[styles.statLabel, { color: theme.textSecondary }]}>
                Total
              </Text>
            </View>
          </View>
        </View>

        {/* Parking Grid */}
        <View style={[styles.card, { backgroundColor: theme.surface }, shadows.md]}>
          <Text style={[styles.cardTitle, { color: theme.textPrimary }]}>
            Parking Spots
          </Text>
          <View style={styles.gridContainer}>
            <ParkingGrid spots={zone.spots} columns={10} onSpotPress={handleSpotPress} />
          </View>
        </View>

        {/* Details Card */}
        <View style={[styles.card, { backgroundColor: theme.surface }, shadows.md]}>
          <Text style={[styles.cardTitle, { color: theme.textPrimary }]}>
            Details
          </Text>

          <View style={styles.detailRow}>
            <Text style={styles.detailIcon}>📍</Text>
            <View style={styles.detailContent}>
              <Text style={[styles.detailLabel, { color: theme.textSecondary }]}>
                Location
              </Text>
              <Text style={[styles.detailValue, { color: theme.textPrimary }]}>
                {zone.latitude.toFixed(4)}, {zone.longitude.toFixed(4)}
              </Text>
            </View>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailIcon}>💳</Text>
            <View style={styles.detailContent}>
              <Text style={[styles.detailLabel, { color: theme.textSecondary }]}>
                Rate
              </Text>
              <Text style={[styles.detailValue, { color: theme.textPrimary }]}>
                $2.00 / hour
              </Text>
            </View>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailIcon}>🕐</Text>
            <View style={styles.detailContent}>
              <Text style={[styles.detailLabel, { color: theme.textSecondary }]}>
                Hours
              </Text>
              <Text style={[styles.detailValue, { color: theme.textPrimary }]}>
                Open 24/7
              </Text>
            </View>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailIcon}>🚗</Text>
            <View style={styles.detailContent}>
              <Text style={[styles.detailLabel, { color: theme.textSecondary }]}>
                Type
              </Text>
              <Text style={[styles.detailValue, { color: theme.textPrimary }]}>
                Street parking
              </Text>
            </View>
          </View>
        </View>

        {/* Bottom Padding */}
        <View style={styles.bottomPadding} />
      </ScrollView>

      {/* Navigate Button (Fixed at bottom) */}
      <View style={[styles.footer, { backgroundColor: theme.surface }, shadows.lg]}>
        <TouchableOpacity
          style={[styles.navigateButton, { backgroundColor: theme.primary }]}
          onPress={() => onNavigate(zone)}
          activeOpacity={0.8}
        >
          <Text style={styles.navigateText}>Start Navigation →</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
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
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  backIcon: {
    fontSize: 28,
    fontWeight: '600',
  },
  headerTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semibold,
  },
  headerRight: {
    width: 40,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: spacing.md,
  },
  section: {
    marginBottom: spacing.md,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    fontSize: 32,
    marginRight: spacing.sm,
  },
  zoneName: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
  },
  card: {
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    marginBottom: spacing.md,
  },
  cardTitle: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold,
    marginBottom: spacing.md,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  progressBackground: {
    flex: 1,
    height: 32,
    borderRadius: borderRadius.lg,
    overflow: 'hidden',
    marginRight: spacing.sm,
  },
  progressFill: {
    height: '100%',
    borderRadius: borderRadius.lg,
  },
  percentage: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
    minWidth: 50,
    textAlign: 'right',
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    marginBottom: spacing.xs,
  },
  statLabel: {
    fontSize: typography.fontSize.sm,
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#E5E5EA',
  },
  gridContainer: {
    alignItems: 'center',
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  detailIcon: {
    fontSize: 24,
    marginRight: spacing.md,
    width: 32,
  },
  detailContent: {
    flex: 1,
  },
  detailLabel: {
    fontSize: typography.fontSize.sm,
    marginBottom: 2,
  },
  detailValue: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.medium,
  },
  bottomPadding: {
    height: 20,
  },
  footer: {
    padding: spacing.md,
    paddingBottom: spacing.lg,
  },
  navigateButton: {
    paddingVertical: spacing.md,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
  },
  navigateText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: '#FFFFFF',
  },
});

export default ParkingDetailScreen;

