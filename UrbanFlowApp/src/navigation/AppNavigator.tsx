/**
 * UrbanFlowAI - App Navigator
 * Stack navigator for app screens
 */

import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import MapScreen from '../screens/MapScreen';
import NavigationScreen from '../screens/NavigationScreen';
import { ParkingZone } from '../services/api';

export type RootStackParamList = {
  Map: undefined;
  Navigation: {
    destination: {
      latitude: number;
      longitude: number;
      name?: string;
    };
  };
};

const Stack = createStackNavigator<RootStackParamList>();

export const AppNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        cardStyle: { backgroundColor: 'transparent' },
      }}
    >
      <Stack.Screen name="Map" component={MapScreen} />
      <Stack.Screen
        name="Navigation"
        component={NavigationScreen}
        options={{
          presentation: 'fullScreenModal',
          animationEnabled: true,
        }}
      />
    </Stack.Navigator>
  );
};

export default AppNavigator;

