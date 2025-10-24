/**
 * UrbanFlowAI - Bottom Sheet
 * Swipeable sheet with 3 states: collapsed, half, expanded
 */

import React, { useCallback, useMemo, useRef } from 'react';
import { View, StyleSheet, useColorScheme } from 'react-native';
import GorhomBottomSheet from '@gorhom/bottom-sheet';
import { colors } from '../../utils/theme';

interface BottomSheetProps {
  children: React.ReactNode;
  snapPoints?: string[];
  initialSnapIndex?: number;
}

export const BottomSheet: React.FC<BottomSheetProps> = ({
  children,
  snapPoints = ['12%', '50%', '90%'], // Collapsed, Half, Expanded
  initialSnapIndex = 0,
}) => {
  const bottomSheetRef = useRef<GorhomBottomSheet>(null);
  const colorScheme = useColorScheme();
  const theme = colorScheme === 'dark' ? colors.dark : colors.light;

  // Memoize snap points
  const snapPointsMemo = useMemo(() => snapPoints, [snapPoints]);

  // Callbacks
  const handleSheetChanges = useCallback((index: number) => {
    console.log('Bottom sheet changed to index:', index);
  }, []);

  return (
    <GorhomBottomSheet
      ref={bottomSheetRef}
      index={initialSnapIndex}
      snapPoints={snapPointsMemo}
      onChange={handleSheetChanges}
      enablePanDownToClose={false}
      backgroundStyle={{
        backgroundColor: theme.surface,
      }}
      handleIndicatorStyle={{
        backgroundColor: theme.border,
        width: 40,
        height: 4,
      }}
      style={styles.bottomSheet}
    >
      <View style={[styles.contentContainer, { backgroundColor: theme.surface }]}>
        {children}
      </View>
    </GorhomBottomSheet>
  );
};

const styles = StyleSheet.create({
  bottomSheet: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: -4,
    },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 10,
  },
  contentContainer: {
    flex: 1,
    paddingHorizontal: 16,
  },
});

export default BottomSheet;

