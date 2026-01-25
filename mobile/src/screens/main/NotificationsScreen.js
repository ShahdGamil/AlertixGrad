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
} from 'react-native-paper';
import api from '../../config/api';
import { colors } from '../../theme/theme';
import Icon from 'react-native-vector-icons/MaterialIcons';

const NotificationsScreen = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    loadNotifications();
    loadUnreadCount();
  }, []);

  const loadNotifications = async () => {
    try {
      const response = await api.get('/notifications');
      setNotifications(response.data.data.notifications);
      setUnreadCount(response.data.data.unreadCount);
    } catch (error) {
      console.error('Notifications load error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const response = await api.get('/notifications/unread-count');
      setUnreadCount(response.data.data.unreadCount);
    } catch (error) {
      console.error('Unread count error:', error);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadNotifications();
    loadUnreadCount();
  };

  const handleMarkAsRead = async (notificationId) => {
    try {
      await api.post(`/notifications/${notificationId}/read`);
      loadNotifications();
      loadUnreadCount();
    } catch (error) {
      console.error('Mark as read error:', error);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return colors.error;
      case 'high':
        return colors.warning;
      case 'medium':
        return colors.info;
      case 'low':
        return colors.success;
      default:
        return colors.textSecondary;
    }
  };

  const renderNotification = ({ item }) => (
    <Card
      style={[styles.card, !item.read && styles.unreadCard]}
      onPress={() => handleMarkAsRead(item.id)}
    >
      <Card.Content>
        <View style={styles.notificationHeader}>
          <View style={styles.notificationInfo}>
            <Text variant="titleMedium" style={styles.notificationTitle}>
              {item.title}
            </Text>
            <Text variant="bodySmall" style={styles.notificationMessage}>
              {item.message}
            </Text>
            <Text variant="bodySmall" style={styles.notificationTime}>
              {new Date(item.timestamp).toLocaleString()}
            </Text>
          </View>
          {item.severity && (
            <Chip
              style={[styles.severityChip, { backgroundColor: getSeverityColor(item.severity) }]}
              textStyle={{ color: '#fff', fontSize: 10 }}
            >
              {item.severity}
            </Chip>
          )}
        </View>
        {item.location && (
          <View style={styles.locationRow}>
            <Icon name="location-on" size={16} color={colors.textSecondary} />
            <Text variant="bodySmall" style={styles.locationText}>
              {item.location}
            </Text>
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
      {unreadCount > 0 && (
        <View style={styles.unreadBadge}>
          <Text variant="bodyMedium" style={styles.unreadText}>
            {unreadCount} unread notification{unreadCount > 1 ? 's' : ''}
          </Text>
        </View>
      )}
      <FlatList
        data={notifications}
        renderItem={renderNotification}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text>No notifications</Text>
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
  unreadBadge: {
    backgroundColor: colors.primary,
    padding: 12,
    alignItems: 'center',
  },
  unreadText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  list: {
    padding: 16,
  },
  card: {
    marginBottom: 16,
  },
  unreadCard: {
    borderLeftWidth: 4,
    borderLeftColor: colors.primary,
  },
  notificationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  notificationInfo: {
    flex: 1,
  },
  notificationTitle: {
    fontWeight: 'bold',
  },
  notificationMessage: {
    color: colors.textSecondary,
    marginTop: 4,
  },
  notificationTime: {
    color: colors.textSecondary,
    marginTop: 4,
    fontSize: 12,
  },
  severityChip: {
    marginLeft: 8,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    gap: 4,
  },
  locationText: {
    color: colors.textSecondary,
  },
  empty: {
    padding: 32,
    alignItems: 'center',
  },
});

export default NotificationsScreen;





