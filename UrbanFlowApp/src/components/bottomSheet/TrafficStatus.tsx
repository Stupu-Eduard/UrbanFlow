/**
 * UrbanFlowAI - Traffic Status Card
 * Displays congestion level and parking availability
 */

import React from 'react';
import { View, Text, StyleSheet, useColorScheme } from 'react-native';
import { colors, typography, spacing } from '../../utils/theme';
import { getCongestionLevel } from '../../utils/theme';

interface TrafficStatusProps {
  averageCongestion: number;
  totalFreeSpots: number;
  totalSpots: number;
  lastUpdated?: string;
}

export const TrafficStatus: React.FC<TrafficStatusProps> = ({
  averageCongestion,
  totalFreeSpots,
  totalSpots,
  lastUpdated,
}) => {
  const colorScheme = useColorScheme();
  const theme = colorScheme === 'dark' ? colors.dark : colors.light;

  const congestionPercent = Math.round(averageCongestion * 100);
  const level = getCongestionLevel(averageCongestion);

  const getLevelEmoji = () => {
    switch (level) {
      case 'low': return '🟢';
      case 'medium': return '🟡';
      case 'high': return '🟠';
      case 'critical': return '🔴';
      default: return '⚪';
    }
  };

  const getLevelText = () => {
    switch (level) {
      case 'low': return 'Low Traffic';
      case 'medium': return 'Moderate';
      case 'high': return 'Heavy Traffic';
      case 'critical': return 'Gridlock';
      default: return 'Unknown';
    }
  };

  const getBarColor = () => {
    if (congestionPercent < 40) return '#10b981';
    if (congestionPercent < 60) return '#f59e0b';
    if (congestionPercent < 80) return '#f97316';
    return '#ef4444';
  };

  return (
    <View style={styles.container}>
      {/* Traffic Section */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={[styles.sectionTitle, { color: theme.textPrimary }]}>
            📊 Traffic Status
          </Text>
          {lastUpdated && (
            <Text style={[styles.timestamp, { color: theme.textSecondary }]}>
              Updated {new Date(lastUpdated).toLocaleTimeString()}
            </Text>
          )}
        </View>

        {/* Congestion Bar */}
        <View style={styles.barContainer}>
          <View style={[styles.barBackground, { backgroundColor: theme.border }]}>
            <View
              style={[
                styles.barFill,
                {
                  width: `${congestionPercent}%`,
                  backgroundColor: getBarColor(),
                },
              ]}
            />
          </View>
          <Text style={[styles.percentage, { color: theme.textPrimary }]}>
            {congestionPercent}%
          </Text>
        </View>

        {/* Level Label */}
        <View style={styles.levelContainer}>
          <Text style={styles.levelEmoji}>{getLevelEmoji()}</Text>
          <Text style={[styles.levelText, { color: theme.textSecondary }]}>
            {getLevelText()}
          </Text>
        </View>
      </View>

      {/* Divider */}
      <View style={[styles.divider, { backgroundColor: theme.border }]} />

      {/* Parking Section */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, { color: theme.textPrimary }]}>
          🅿️ Available Parking
        </Text>
        <View style={styles.parkingInfo}>
          <Text style={[styles.parkingCount, { color: theme.primary }]}>
            {totalFreeSpots}
          </Text>
          <Text style={[styles.parkingLabel, { color: theme.textSecondary }]}>
            of {totalSpots} spots free nearby
          </Text>
        </View>
      </View>

      {/* Hint */}
      <Text style={[styles.hint, { color: theme.textSecondary }]}>
        ↑ Swipe up for parking details
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: spacing.md,
  },
  section: {
    marginBottom: spacing.sm,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  sectionTitle: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold,
  },
  timestamp: {
    fontSize: typography.fontSize.xs,
  },
  barContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  barBackground: {
    flex: 1,
    height: 32,
    borderRadius: 16,
    overflow: 'hidden',
    marginRight: spacing.sm,
  },
  barFill: {
    height: '100%',
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  percentage: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
    minWidth: 50,
    textAlign: 'right',
  },
  levelContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  levelEmoji: {
    fontSize: 20,
    marginRight: spacing.xs,
  },
  levelText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium,
    textTransform: 'uppercase',
  },
  divider: {
    height: 1,
    marginVertical: spacing.md,
  },
  parkingInfo: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginTop: spacing.xs,
  },
  parkingCount: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    marginRight: spacing.xs,
  },
  parkingLabel: {
    fontSize: typography.fontSize.sm,
  },
  hint: {
    fontSize: typography.fontSize.xs,
    textAlign: 'center',
    marginTop: spacing.sm,
    fontStyle: 'italic',
  },
});

export default TrafficStatus;

