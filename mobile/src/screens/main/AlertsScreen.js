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
  Menu,
} from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import api from '../../config/api';
import { colors } from '../../theme/theme';
import Icon from 'react-native-vector-icons/MaterialIcons';

const AlertsScreen = ({ navigation }) => {
  const { user } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState('all');
  const [menuVisible, setMenuVisible] = useState(false);

  useEffect(() => {
    loadAlerts();
  }, [filter]);

  const loadAlerts = async () => {
    try {
      const params = { limit: 50 };
      if (filter !== 'all') {
        params.status = filter;
      }
      const response = await api.get('/alerts', { params });
      setAlerts(response.data.data.alerts);
    } catch (error) {
      console.error('Alerts load error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadAlerts();
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

  const renderAlert = ({ item }) => (
    <Card
      style={styles.card}
      onPress={() => navigation.navigate('AlertDetail', { alertId: item._id })}
    >
      <Card.Content>
        <View style={styles.alertHeader}>
          <View style={styles.alertInfo}>
            <Text variant="titleMedium" style={styles.alertType}>
              {item.type?.toUpperCase()}
            </Text>
            <Text variant="bodySmall" style={styles.alertCamera}>
              {item.camera?.name || 'Unknown Camera'}
            </Text>
            <Text variant="bodySmall" style={styles.alertTime}>
              {new Date(item.detectedAt).toLocaleString()}
            </Text>
          </View>
          <Chip
            style={[styles.severityChip, { backgroundColor: getSeverityColor(item.severity) }]}
            textStyle={{ color: '#fff', fontSize: 10 }}
          >
            {item.severity}
          </Chip>
        </View>
        {item.description && (
          <Text variant="bodySmall" style={styles.alertDescription}>
            {item.description}
          </Text>
        )}
        <View style={styles.alertFooter}>
          <Chip
            style={[
              styles.statusChip,
              {
                backgroundColor:
                  item.status === 'open'
                    ? colors.error
                    : item.status === 'acknowledged'
                    ? colors.warning
                    : colors.success,
              },
            ]}
            textStyle={{ color: '#fff', fontSize: 10 }}
          >
            {item.status}
          </Chip>
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
              {filter === 'all' ? 'All Alerts' : filter}
            </Chip>
          }
        >
          <Menu.Item onPress={() => { setFilter('all'); setMenuVisible(false); }} title="All" />
          <Menu.Item onPress={() => { setFilter('open'); setMenuVisible(false); }} title="Open" />
          <Menu.Item onPress={() => { setFilter('acknowledged'); setMenuVisible(false); }} title="Acknowledged" />
          <Menu.Item onPress={() => { setFilter('closed'); setMenuVisible(false); }} title="Closed" />
        </Menu>
      </View>

      <FlatList
        data={alerts}
        renderItem={renderAlert}
        keyExtractor={(item) => item._id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text>No alerts found</Text>
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
    marginBottom: 16,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  alertInfo: {
    flex: 1,
  },
  alertType: {
    fontWeight: 'bold',
  },
  alertCamera: {
    color: colors.textSecondary,
    marginTop: 4,
  },
  alertTime: {
    color: colors.textSecondary,
    marginTop: 4,
  },
  severityChip: {
    marginLeft: 8,
  },
  alertDescription: {
    marginTop: 8,
    color: colors.textSecondary,
  },
  alertFooter: {
    marginTop: 12,
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  statusChip: {
    marginLeft: 8,
  },
  empty: {
    padding: 32,
    alignItems: 'center',
  },
});

export default AlertsScreen;





