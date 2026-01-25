import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  RefreshControl,
} from 'react-native';
import {
  Card,
  Text,
  ActivityIndicator,
  Chip,
  FAB,
} from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import api from '../../config/api';
import { colors } from '../../theme/theme';
import Icon from 'react-native-vector-icons/MaterialIcons';

const CamerasScreen = ({ navigation }) => {
  const { user } = useAuth();
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadCameras();
  }, []);

  const loadCameras = async () => {
    try {
      const response = await api.get('/cameras?limit=100');
      setCameras(response.data.data.cameras);
    } catch (error) {
      console.error('Cameras load error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadCameras();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'online':
        return colors.online;
      case 'offline':
        return colors.offline;
      case 'maintenance':
        return colors.maintenance;
      default:
        return colors.textSecondary;
    }
  };

  const renderCamera = ({ item }) => (
    <Card
      style={styles.card}
      onPress={() => navigation.navigate('CameraDetail', { cameraId: item._id })}
    >
      <Card.Content>
        <View style={styles.cameraHeader}>
          <View style={styles.cameraInfo}>
            <Text variant="titleMedium" style={styles.cameraName}>
              {item.name}
            </Text>
            <Text variant="bodySmall" style={styles.cameraLocation}>
              {item.location}
            </Text>
          </View>
          <Chip
            style={[styles.statusChip, { backgroundColor: getStatusColor(item.status) }]}
            textStyle={{ color: '#fff' }}
          >
            {item.status}
          </Chip>
        </View>
        <View style={styles.cameraDetails}>
          <View style={styles.detailRow}>
            <Icon name="location-on" size={16} color={colors.textSecondary} />
            <Text variant="bodySmall" style={styles.detailText}>
              {item.ipAddress}
            </Text>
          </View>
          {item.aiEnabled && (
            <View style={styles.detailRow}>
              <Icon name="smart-toy" size={16} color={colors.primary} />
              <Text variant="bodySmall" style={styles.detailText}>
                AI Enabled
              </Text>
            </View>
          )}
        </View>
      </Card.Content>
    </Card>
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={cameras}
        renderItem={renderCamera}
        keyExtractor={(item) => item._id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text>No cameras found</Text>
          </View>
        }
      />
      {(user?.role === 'admin' || user?.role === 'operator') && (
        <FAB
          icon="plus"
          style={styles.fab}
          onPress={() => {
            // Navigate to add camera screen
            navigation.navigate('CameraDetail', { cameraId: null });
          }}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  list: {
    padding: 16,
  },
  card: {
    marginBottom: 16,
  },
  cameraHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  cameraInfo: {
    flex: 1,
  },
  cameraName: {
    fontWeight: 'bold',
  },
  cameraLocation: {
    color: colors.textSecondary,
    marginTop: 4,
  },
  statusChip: {
    marginLeft: 8,
  },
  cameraDetails: {
    marginTop: 8,
    gap: 8,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  detailText: {
    color: colors.textSecondary,
  },
  empty: {
    padding: 32,
    alignItems: 'center',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
});

export default CamerasScreen;





