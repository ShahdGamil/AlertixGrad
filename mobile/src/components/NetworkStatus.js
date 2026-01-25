import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import NetInfo from '@react-native-community/netinfo';

/**
 * Network Status Banner Component
 *
 * Displays a banner when device loses internet connectivity.
 * Automatically hides when connection is restored.
 *
 * Usage:
 * ```jsx
 * <NetworkStatus />
 * ```
 */
const NetworkStatus = () => {
  const [isConnected, setIsConnected] = useState(true);
  const [slideAnim] = useState(new Animated.Value(-100));

  useEffect(() => {
    // Subscribe to network state updates
    const unsubscribe = NetInfo.addEventListener((state) => {
      const connected = state.isConnected && state.isInternetReachable;
      setIsConnected(connected);

      // Animate banner in/out
      if (!connected) {
        // Show banner
        Animated.timing(slideAnim, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }).start();
      } else {
        // Hide banner
        Animated.timing(slideAnim, {
          toValue: -100,
          duration: 300,
          useNativeDriver: true,
        }).start();
      }
    });

    // Cleanup subscription
    return () => unsubscribe();
  }, []);

  return (
    <Animated.View
      style={[
        styles.container,
        {
          transform: [{ translateY: slideAnim }],
        },
      ]}
    >
      <View style={styles.banner}>
        <Text style={styles.icon}>📡</Text>
        <Text style={styles.text}>No Internet Connection</Text>
      </View>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 9999,
  },
  banner: {
    backgroundColor: '#D32F2F',
    paddingVertical: 12,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  icon: {
    fontSize: 18,
    marginRight: 8,
  },
  text: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
});

export default NetworkStatus;
