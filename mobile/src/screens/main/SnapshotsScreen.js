import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  RefreshControl,
  Image,
  Dimensions,
} from 'react-native';
import {
  Card,
  Text,
  ActivityIndicator,
  Menu,
  Chip,
} from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import api from '../../config/api';
import { colors } from '../../theme/theme';

const { width } = Dimensions.get('window');
const imageSize = (width - 48) / 2;

const SnapshotsScreen = () => {
  const { user } = useAuth();
  const [snapshots, setSnapshots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState('all');
  const [menuVisible, setMenuVisible] = useState(false);

  useEffect(() => {
    loadSnapshots();
  }, [filter]);

  const loadSnapshots = async () => {
    try {
      const params = { limit: 50 };
      if (filter !== 'all') {
        params.camera = filter;
      }
      const response = await api.get('/snapshots', { params });
      setSnapshots(response.data.data.snapshots);
    } catch (error) {
      console.error('Snapshots load error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadSnapshots();
  };

  const renderSnapshot = ({ item }) => (
    <Card style={styles.card}>
      <View style={styles.imageContainer}>
        <Image
          source={{ uri: item.thumbnailUrl || item.imageUrl || 'https://via.placeholder.com/300' }}
          style={styles.image}
        />
      </View>
      <Card.Content>
        <Text variant="bodySmall" style={styles.cameraName}>
          {item.camera?.name}
        </Text>
        <Text variant="bodySmall" style={styles.timestamp}>
          {new Date(item.capturedAt).toLocaleString()}
        </Text>
        {item.tags && item.tags.length > 0 && (
          <View style={styles.tagsContainer}>
            {item.tags.map((tag, index) => (
              <Chip key={index} style={styles.tag} textStyle={{ fontSize: 10 }}>
                {tag}
              </Chip>
            ))}
          </View>
        )}
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
      <View style={styles.filterBar}>
        <Menu
          visible={menuVisible}
          onDismiss={() => setMenuVisible(false)}
          anchor={
            <Chip
              icon="filter-list"
              onPress={() => setMenuVisible(true)}
              style={styles.filterChip}
            >
              Filter
            </Chip>
          }
        >
          <Menu.Item onPress={() => { setFilter('all'); setMenuVisible(false); }} title="All" />
        </Menu>
      </View>

      <FlatList
        data={snapshots}
        renderItem={renderSnapshot}
        keyExtractor={(item) => item._id}
        numColumns={2}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text>No snapshots found</Text>
          </View>
        }
      />
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
  filterBar: {
    padding: 16,
    backgroundColor: colors.surface,
  },
  filterChip: {
    alignSelf: 'flex-start',
  },
  list: {
    padding: 16,
  },
  card: {
    width: imageSize,
    margin: 4,
  },
  imageContainer: {
    width: '100%',
    height: imageSize,
    backgroundColor: colors.border,
  },
  image: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  cameraName: {
    fontWeight: 'bold',
    marginTop: 8,
  },
  timestamp: {
    color: colors.textSecondary,
    marginTop: 4,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
    gap: 4,
  },
  tag: {
    marginRight: 4,
    marginBottom: 4,
  },
  empty: {
    padding: 32,
    alignItems: 'center',
  },
});

export default SnapshotsScreen;

