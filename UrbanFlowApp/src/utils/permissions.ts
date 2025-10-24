/**
 * UrbanFlowAI - Location Permissions
 * Handle location permission requests for Android & iOS
 */

import { Platform, PermissionsAndroid, Alert } from 'react-native';

export const requestLocationPermission = async (): Promise<boolean> => {
  try {
    if (Platform.OS === 'android') {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
        {
          title: 'Location Permission',
          message:
            'UrbanFlowAI needs access to your location to show real-time traffic, nearby parking, and provide navigation.',
          buttonNeutral: 'Ask Me Later',
          buttonNegative: 'Cancel',
          buttonPositive: 'OK',
        }
      );

      if (granted === PermissionsAndroid.RESULTS.GRANTED) {
        console.log('✅ Location permission granted');
        return true;
      } else {
        console.log('❌ Location permission denied');
        Alert.alert(
          'Location Permission Required',
          'To use UrbanFlowAI, please enable location access in your device settings.',
          [{ text: 'OK' }]
        );
        return false;
      }
    } else {
      // iOS - permission is requested automatically when location is accessed
      // If denied, user must enable it in Settings
      return true;
    }
  } catch (err) {
    console.warn('Error requesting location permission:', err);
    return false;
  }
};

export const checkLocationPermission = async (): Promise<boolean> => {
  try {
    if (Platform.OS === 'android') {
      const granted = await PermissionsAndroid.check(
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
      );
      return granted;
    } else {
      // iOS - will be checked when trying to access location
      return true;
    }
  } catch (err) {
    console.warn('Error checking location permission:', err);
    return false;
  }
};

