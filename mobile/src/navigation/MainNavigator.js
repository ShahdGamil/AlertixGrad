import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useAuth } from '../context/AuthContext';
import { colors } from '../theme/theme';

// Screens
import DashboardScreen from '../screens/main/DashboardScreen';
import CamerasScreen from '../screens/main/CamerasScreen';
import CameraDetailScreen from '../screens/main/CameraDetailScreen';
import CameraLiveViewScreen from '../screens/main/CameraLiveViewScreen';
import AlertsScreen from '../screens/main/AlertsScreen';
import AlertDetailScreen from '../screens/main/AlertDetailScreen';
import SnapshotsScreen from '../screens/main/SnapshotsScreen';
// Reports page removed per requirements
import SettingsScreen from '../screens/main/SettingsScreenNew';
import UserManagementScreen from '../screens/main/UserManagementScreenNew';
import AddUserScreen from '../screens/main/AddUserScreen';
import BillingScreen from '../screens/main/BillingScreen';
import NotificationsScreen from '../screens/main/NotificationsScreen';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

const CameraStack = () => (
  <Stack.Navigator>
    <Stack.Screen 
      name="CameraList" 
      component={CamerasScreen}
      options={{ title: 'Cameras' }}
    />
    <Stack.Screen 
      name="CameraDetail" 
      component={CameraDetailScreen}
      options={{ title: 'Camera Details' }}
    />
    <Stack.Screen 
      name="CameraLiveView" 
      component={CameraLiveViewScreen}
      options={{ title: 'Live View' }}
    />
  </Stack.Navigator>
);

const AlertStack = () => (
  <Stack.Navigator>
    <Stack.Screen 
      name="AlertList" 
      component={AlertsScreen}
      options={{ title: 'Alerts' }}
    />
    <Stack.Screen 
      name="AlertDetail" 
      component={AlertDetailScreen}
      options={{ title: 'Alert Details' }}
    />
  </Stack.Navigator>
);

const SettingsStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerStyle: {
        backgroundColor: colors.primary,
      },
      headerTintColor: '#fff',
      headerTitleStyle: {
        fontWeight: 'bold',
      },
    }}
  >
    <Stack.Screen 
      name="SettingsMain" 
      component={SettingsScreen}
      options={{ title: 'Settings', headerShown: false }}
    />
    <Stack.Screen 
      name="UserManagement" 
      component={UserManagementScreen}
      options={{ title: 'User Management' }}
    />
    <Stack.Screen 
      name="AddUser" 
      component={AddUserScreen}
      options={{ title: 'Add User' }}
    />
  </Stack.Navigator>
);

const MainNavigator = () => {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';
  const isOperator = user?.role === 'operator' || isAdmin;

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Dashboard') {
            iconName = 'dashboard';
          } else if (route.name === 'Cameras') {
            iconName = 'videocam';
          } else if (route.name === 'Alerts') {
            iconName = 'notifications';
          } else if (route.name === 'Snapshots') {
            iconName = 'photo-library';
          } else if (route.name === 'Settings') {
            iconName = 'settings';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        headerShown: false,
      })}
    >
      <Tab.Screen name="Dashboard" component={DashboardScreen} />
      <Tab.Screen name="Cameras" component={CameraStack} />
      <Tab.Screen name="Alerts" component={AlertStack} />
      {(isOperator || isAdmin) && (
        <Tab.Screen name="Snapshots" component={SnapshotsScreen} />
      )}
      <Tab.Screen name="Settings" component={SettingsStack} />
    </Tab.Navigator>
  );
};

export default MainNavigator;

