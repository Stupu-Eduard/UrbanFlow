/**
 * UrbanFlowAI - Design System & Theme
 * Apple Maps-inspired design tokens
 */

import { Platform } from 'react-native';

export const colors = {
  light: {
    background: '#FFFFFF',
    surface: '#F5F5F7',
    primary: '#007AFF', // Apple blue
    success: '#34C759', // Green - available parking
    warning: '#FF9500', // Orange - moderate traffic
    danger: '#FF3B30', // Red - critical traffic
    textPrimary: '#000000',
    textSecondary: '#8E8E93',
    border: '#C6C6C8',
    overlay: 'rgba(0, 0, 0, 0.3)',
    cardBackground: '#FFFFFF',
    cardShadow: 'rgba(0, 0, 0, 0.1)',
  },
  dark: {
    background: '#000000',
    surface: '#1C1C1E',
    primary: '#0A84FF',
    success: '#30D158',
    warning: '#FF9F0A',
    danger: '#FF453A',
    textPrimary: '#FFFFFF',
    textSecondary: '#8E8E93',
    border: '#38383A',
    overlay: 'rgba(255, 255, 255, 0.2)',
    cardBackground: '#1C1C1E',
    cardShadow: 'rgba(255, 255, 255, 0.05)',
  },
};

export const typography = {
  fontFamily: {
    regular: Platform.select({
      ios: 'SF Pro Text',
      android: 'Roboto',
      default: 'System',
    }),
    medium: Platform.select({
      ios: 'SF Pro Text',
      android: 'Roboto-Medium',
      default: 'System',
    }),
    semibold: Platform.select({
      ios: 'SF Pro Text',
      android: 'Roboto-Medium',
      default: 'System',
    }),
    bold: Platform.select({
      ios: 'SF Pro Text',
      android: 'Roboto-Bold',
      default: 'System',
    }),
  },
  fontSize: {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 24,
    '2xl': 32,
  },
  fontWeight: {
    regular: '400' as const,
    medium: '500' as const,
    semibold: '600' as const,
    bold: '700' as const,
  },
  lineHeight: {
    xs: 16,
    sm: 20,
    base: 24,
    lg: 28,
    xl: 32,
    '2xl': 40,
  },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
};

export const borderRadius = {
  sm: 6,
  md: 8,
  lg: 12,
  xl: 16,
  '2xl': 24,
  full: 9999,
};

export const shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 4,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 15,
    elevation: 8,
  },
  xl: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 20 },
    shadowOpacity: 0.2,
    shadowRadius: 25,
    elevation: 12,
  },
};

export const animation = {
  duration: {
    fast: 200,
    normal: 300,
    slow: 500,
  },
  easing: {
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
  },
};

// Traffic congestion colors (for heat map)
export const trafficColors = {
  low: '#10b981', // Green (0-40%)
  medium: '#f59e0b', // Yellow (40-60%)
  high: '#f97316', // Orange (60-80%)
  critical: '#ef4444', // Red (80-100%)
};

// Parking occupancy colors
export const parkingColors = {
  available: '#10b981', // Green (< 50% full)
  moderate: '#f59e0b', // Yellow (50-80% full)
  full: '#ef4444', // Red (> 80% full)
};

// Get congestion color based on score (0-1)
export const getCongestionColor = (score: number): string => {
  if (score < 0.4) return trafficColors.low;
  if (score < 0.6) return trafficColors.medium;
  if (score < 0.8) return trafficColors.high;
  return trafficColors.critical;
};

// Get congestion level label
export const getCongestionLevel = (score: number): string => {
  if (score < 0.4) return 'low';
  if (score < 0.6) return 'medium';
  if (score < 0.8) return 'high';
  return 'critical';
};

// Get parking color based on occupancy rate (0-1)
export const getParkingColor = (occupancyRate: number): string => {
  if (occupancyRate < 0.5) return parkingColors.available;
  if (occupancyRate < 0.8) return parkingColors.moderate;
  return parkingColors.full;
};

export const theme = {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  animation,
  trafficColors,
  parkingColors,
  getCongestionColor,
  getCongestionLevel,
  getParkingColor,
};

export default theme;

