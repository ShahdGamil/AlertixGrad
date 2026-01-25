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
  Menu,
} from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import api from '../../config/api';
import { colors } from '../../theme/theme';

const UserManagementScreen = ({ navigation }) => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await api.get('/users');
      setUsers(response.data.data.users);
    } catch (error) {
      console.error('Users load error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadUsers();
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin':
        return colors.error;
      case 'operator':
        return colors.warning;
      case 'viewer':
        return colors.info;
      default:
        return colors.textSecondary;
    }
  };

  const renderUser = ({ item }) => (
    <Card style={styles.card}>
      <Card.Content>
        <View style={styles.userHeader}>
          <View style={styles.userInfo}>
            <Text variant="titleMedium" style={styles.userName}>
              {item.name}
            </Text>
            <Text variant="bodySmall" style={styles.userEmail}>
              {item.email}
            </Text>
          </View>
          <Chip
            style={[styles.roleChip, { backgroundColor: getRoleColor(item.role) }]}
            textStyle={{ color: '#fff' }}
          >
            {item.role}
          </Chip>
        </View>
        <View style={styles.userDetails}>
          <Text variant="bodySmall" style={styles.detailText}>
            Status: {item.isActive ? 'Active' : 'Inactive'}
          </Text>
          {item.lastLogin && (
            <Text variant="bodySmall" style={styles.detailText}>
              Last Login: {new Date(item.lastLogin).toLocaleString()}
            </Text>
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
        data={users}
        renderItem={renderUser}
        keyExtractor={(item) => item._id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text>No users found</Text>
          </View>
        }
      />
      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => {
          // Navigate to add user screen
        }}
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
  list: {
    padding: 16,
  },
  card: {
    marginBottom: 16,
  },
  userHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontWeight: 'bold',
  },
  userEmail: {
    color: colors.textSecondary,
    marginTop: 4,
  },
  roleChip: {
    marginLeft: 8,
  },
  userDetails: {
    marginTop: 8,
    gap: 4,
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

export default UserManagementScreen;





