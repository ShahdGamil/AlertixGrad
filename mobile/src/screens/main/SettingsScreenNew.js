import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
} from 'react-native';
import {
  Card,
  Text,
  ActivityIndicator,
  Button,
  Switch,
  TextInput,
  Divider,
} from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import api from '../../config/api';
import { colors } from '../../theme/theme';
import Icon from 'react-native-vector-icons/MaterialIcons';

const SettingsScreenNew = ({ navigation }) => {
  const { user, logout } = useAuth();
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [alertEnabled, setAlertEnabled] = useState(true);
  const [motionDetection, setMotionDetection] = useState(true);
  const [soundAlerts, setSoundAlerts] = useState(true);
  const [emailNotifications, setEmailNotifications] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await api.get('/settings');
      const settingsData = response.data.data.settings;
      setSettings(settingsData);
      setAlertEnabled(settingsData?.alertThresholds?.theft?.enabled ?? true);
      setMotionDetection(settingsData?.alertThresholds?.motion?.enabled ?? true);
      setSoundAlerts(true);
      setEmailNotifications(settingsData?.notificationPreferences?.email?.enabled ?? false);
    } catch (error) {
      console.error('Settings load error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put('/settings', {
        alertThresholds: {
          theft: { enabled: alertEnabled },
          motion: { enabled: motionDetection }
        },
        notificationPreferences: {
          email: { enabled: emailNotifications }
        }
      });
      // Show success message
    } catch (error) {
      console.error('Save error:', error);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text variant="headlineMedium" style={styles.headerTitle}>Settings</Text>
        <Button
          mode="contained"
          buttonColor={colors.error}
          onPress={logout}
          style={styles.logoutButton}
          icon="logout"
        >
          Logout
        </Button>
      </View>

      {/* Profile Section */}
      <Card style={styles.card}>
        <Card.Title
          title="Profile"
          left={(props) => <Icon {...props} name="person" size={24} color={colors.primary} />}
        />
        <Card.Content>
          <TextInput
            label="Username"
            value={user?.name || ''}
            mode="outlined"
            style={styles.input}
            editable={false}
          />
          <TextInput
            label="Role"
            value={user?.role?.toUpperCase() || ''}
            mode="outlined"
            style={styles.input}
            editable={false}
          />
          <TextInput
            label="Email"
            value={user?.email || ''}
            mode="outlined"
            style={styles.input}
            editable={false}
          />
        </Card.Content>
      </Card>

      {/* Alert Settings Section */}
      <Card style={styles.card}>
        <Card.Title
          title="Alert Settings"
          left={(props) => <Icon {...props} name="notifications" size={24} color={colors.warning} />}
        />
        <Card.Content>
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text variant="bodyLarge" style={styles.settingLabel}>Enable Alerts</Text>
              <Text variant="bodySmall" style={styles.settingDesc}>
                Turn all alerts on or off.
              </Text>
            </View>
            <Switch
              value={alertEnabled}
              onValueChange={setAlertEnabled}
            />
          </View>

          <Divider style={styles.divider} />

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text variant="bodyLarge" style={styles.settingLabel}>Motion Detection</Text>
              <Text variant="bodySmall" style={styles.settingDesc}>
                Detect motion in camera feeds.
              </Text>
            </View>
            <Switch
              value={motionDetection}
              onValueChange={setMotionDetection}
            />
          </View>

          <Divider style={styles.divider} />

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text variant="bodyLarge" style={styles.settingLabel}>Sound Alerts</Text>
              <Text variant="bodySmall" style={styles.settingDesc}>
                Play sound when alert triggered.
              </Text>
            </View>
            <Switch
              value={soundAlerts}
              onValueChange={setSoundAlerts}
            />
          </View>

          <Divider style={styles.divider} />

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text variant="bodyLarge" style={styles.settingLabel}>Email Notifications</Text>
              <Text variant="bodySmall" style={styles.settingDesc}>
                Send alerts via email.
              </Text>
            </View>
            <Switch
              value={emailNotifications}
              onValueChange={setEmailNotifications}
            />
          </View>
        </Card.Content>
      </Card>

      {/* User Management Section (Admin only) */}
      {user?.role === 'admin' && (
        <Card style={styles.card}>
          <Card.Title
            title="User Management"
            left={(props) => <Icon {...props} name="people" size={24} color={colors.success} />}
            right={(props) => (
              <Button
                mode="contained"
                onPress={() => {
                  try {
                    navigation.navigate('AddUser');
                  } catch (error) {
                    console.error('Navigation error from Settings:', error);
                    navigation.navigate('UserManagement', { screen: 'AddUser' });
                  }
                }}
                style={styles.addUserButton}
                icon="plus"
                compact
                buttonColor={colors.primary}
              >
                Add User
              </Button>
            )}
          />
          <Card.Content>
            <Button
              mode="outlined"
              onPress={() => navigation.navigate('UserManagement')}
              style={styles.viewUsersButton}
              icon="arrow-forward"
            >
              View All Users
            </Button>
          </Card.Content>
        </Card>
      )}

      {/* Save Button */}
      {user?.role === 'admin' && (
        <Button
          mode="contained"
          onPress={handleSave}
          style={styles.saveButton}
          loading={saving}
        >
          Save Settings
        </Button>
      )}
    </ScrollView>
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: colors.surface,
  },
  headerTitle: {
    fontWeight: 'bold',
  },
  logoutButton: {
    marginLeft: 'auto',
  },
  card: {
    margin: 16,
    marginTop: 0,
  },
  input: {
    marginBottom: 16,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
  },
  settingLabel: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  settingDesc: {
    color: colors.textSecondary,
  },
  divider: {
    marginVertical: 8,
  },
  addUserButton: {
    marginRight: 8,
  },
  viewUsersButton: {
    marginTop: 8,
  },
  saveButton: {
    margin: 16,
    marginTop: 0,
  },
});

export default SettingsScreenNew;

