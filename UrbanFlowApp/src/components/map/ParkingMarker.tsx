/**
 * UrbanFlowAI - Parking Marker
 * Custom parking pin with occupancy indicator
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import MapboxGL from '@rnmapbox/maps';
import { ParkingZone } from '../../services/api';
import { getParkingColor } from '../../utils/theme';

interface ParkingMarkerProps {
  zone: ParkingZone;
  onPress: (zone: ParkingZone) => void;
}

export const ParkingMarker: React.FC<ParkingMarkerProps> = ({ zone, onPress }) => {
  const occupancyRate = zone.occupancy_rate;
  const color = getParkingColor(occupancyRate);
  const percentage = Math.round(occupancyRate * 100);

  return (
    <MapboxGL.MarkerView
      id={zone.zone_id}
      coordinate={[zone.longitude, zone.latitude]}
      anchor={{ x: 0.5, y: 1 }}
    >
      <TouchableOpacity
        onPress={() => onPress(zone)}
        style={styles.markerContainer}
        activeOpacity={0.7}
      >
        {/* Pin Body */}
        <View style={[styles.pinBody, { backgroundColor: color }]}>
          <Text style={styles.parkingIcon}>🅿️</Text>
          <Text style={styles.occupancyText}>{percentage}%</Text>
        </View>

        {/* Pin Tip */}
        <View style={[styles.pinTip, { borderTopColor: color }]} />

        {/* Badge with free spots */}
        {zone.free_spots > 0 && (
          <View style={[styles.badge, { backgroundColor: color }]}>
            <Text style={styles.badgeText}>{zone.free_spots}</Text>
          </View>
        )}
      </TouchableOpacity>
    </MapboxGL.MarkerView>
  );
};

const styles = StyleSheet.create({
  markerContainer: {
    alignItems: 'center',
  },
  pinBody: {
    width: 50,
    height: 50,
    borderRadius: 25,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 3,
    borderColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  parkingIcon: {
    fontSize: 16,
    marginBottom: 2,
  },
  occupancyText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  pinTip: {
    width: 0,
    height: 0,
    borderLeftWidth: 10,
    borderRightWidth: 10,
    borderTopWidth: 12,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    marginTop: -1,
  },
  badge: {
    position: 'absolute',
    top: -8,
    right: -8,
    width: 24,
    height: 24,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});

export default ParkingMarker;

