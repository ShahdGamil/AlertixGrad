import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import {
  Card,
  Text,
  ActivityIndicator,
  Chip,
  FAB,
  Button,
} from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import api from '../../config/api';
import { colors } from '../../theme/theme';
import Icon from 'react-native-vector-icons/MaterialIcons';

const UserManagementScreenNew = ({ navigation }) => {
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
        return '#1976D2'; // Dark blue
      case 'operator':
        return colors.warning;
      case 'viewer':
        return colors.info;
      default:
        return colors.textSecondary;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'numeric', day: 'numeric', year: 'numeric' });
  };

  const renderUser = ({ item }) => (
    <TouchableOpacity
      onPress={() => navigation.navigate('AddUser', { user: item })}
      activeOpacity={0.7}
    >
      <Card style={styles.userCard}>
        <Card.Content style={styles.userContent}>
          <View style={styles.userIconContainer}>
            <View style={styles.userIconCircle}>
              <Icon name="person" size={24} color="#fff" />
            </View>
          </View>
          <View style={styles.userInfo}>
            <Text variant="titleMedium" style={styles.userName}>
              {item.name}
            </Text>
            <Text variant="bodySmall" style={styles.userEmail}>
              {item.email}
            </Text>
          </View>
          <View style={styles.userRoleContainer}>
            <Chip
              style={[styles.roleChip, { backgroundColor: getRoleColor(item.role) }]}
              textStyle={{ color: '#fff', fontSize: 12, fontWeight: '500' }}
            >
              {item.role}
            </Chip>
            <Text variant="bodySmall" style={styles.userDate}>
              Added {formatDate(item.createdAt)}
            </Text>
          </View>
        </Card.Content>
      </Card>
    </TouchableOpacity>
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
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <View style={styles.headerIcon}>
            <Icon name="people" size={24} color="#fff" />
          </View>
          <Text variant="headlineSmall" style={styles.headerTitle}>
            User Management
          </Text>
        </View>
        <Button
          mode="contained"
          onPress={() => {
            try {
              console.log('Add User button pressed, navigating...');
              navigation.navigate('AddUser');
            } catch (error) {
              console.error('Navigation error:', error);
              if (navigation.getParent) {
                navigation.getParent()?.navigate('AddUser');
              }
            }
          }}
          style={styles.addButton}
          buttonColor={colors.primary}
          icon="plus"
          contentStyle={styles.addButtonContent}
          labelStyle={styles.addButtonLabel}
        >
          Add User
        </Button>
      </View>

      {/* User List */}
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
            <Text style={styles.emptyText}>No users found</Text>
          </View>
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212', // Dark background
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#121212',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#121212',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  headerIcon: {
    width: 40,
    height: 40,
    borderRadius: 8,
    backgroundColor: colors.success,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  headerTitle: {
    color: '#fff',
    fontWeight: 'bold',
  },
  addButton: {
    borderRadius: 8,
  },
  addButtonContent: {
    paddingVertical: 4,
    paddingHorizontal: 8,
  },
  addButtonLabel: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  list: {
    padding: 16,
    paddingTop: 8,
  },
  userCard: {
    marginBottom: 12,
    backgroundColor: '#1E1E1E', // Dark gray card
    borderRadius: 12,
    elevation: 2,
  },
  userContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
  },
  userIconContainer: {
    marginRight: 16,
  },
  userIconCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#424242', // Gray circle
    justifyContent: 'center',
    alignItems: 'center',
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    color: '#fff',
    fontWeight: 'bold',
    marginBottom: 4,
  },
  userEmail: {
    color: '#B0B0B0', // Light gray
  },
  userRoleContainer: {
    alignItems: 'flex-end',
    marginLeft: 12,
  },
  roleChip: {
    marginBottom: 8,
    height: 28,
    borderRadius: 6,
    paddingHorizontal: 8,
  },
  userDate: {
    color: '#B0B0B0',
    fontSize: 12,
  },
  empty: {
    padding: 32,
    alignItems: 'center',
  },
  emptyText: {
    color: '#B0B0B0',
  },
});

export default UserManagementScreenNew;
