import { useState, useEffect } from 'react';
import NetInfo from '@react-native-community/netinfo';

/**
 * Custom Hook: useNetworkStatus
 *
 * Monitor network connectivity status in real-time.
 *
 * @returns {Object} Network status information
 * - isConnected: {boolean} Whether device has internet connection
 * - connectionType: {string} Type of connection (wifi, cellular, etc.)
 * - isInternetReachable: {boolean} Whether internet is actually reachable
 *
 * Usage:
 * ```jsx
 * const { isConnected, connectionType, isInternetReachable } = useNetworkStatus();
 *
 * if (!isConnected) {
 *   return <OfflineMessage />;
 * }
 * ```
 */
const useNetworkStatus = () => {
  const [networkState, setNetworkState] = useState({
    isConnected: true,
    connectionType: 'unknown',
    isInternetReachable: true,
  });

  useEffect(() => {
    // Get initial network state
    NetInfo.fetch().then((state) => {
      setNetworkState({
        isConnected: state.isConnected,
        connectionType: state.type,
        isInternetReachable: state.isInternetReachable,
      });
    });

    // Subscribe to network state updates
    const unsubscribe = NetInfo.addEventListener((state) => {
      setNetworkState({
        isConnected: state.isConnected,
        connectionType: state.type,
        isInternetReachable: state.isInternetReachable,
      });
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, []);

  return networkState;
};

export default useNetworkStatus;
