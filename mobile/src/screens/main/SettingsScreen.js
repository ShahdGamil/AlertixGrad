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

const SettingsScreen = ({ navigation }) => {
  const { user, logout } = useAuth();
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await api.get('/settings');
      setSettings(response.data.data.settings);
    } catch (error) {
      console.error('Settings load error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put('/settings', settings);
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

  if (!settings) {
    return (
      <View style={styles.center}>
        <Text>Settings not found</Text>
      </View>
    );
  }

  const isAdmin = user?.role === 'admin';

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Title title="Profile" />
        <Card.Content>
          <View style={styles.profileRow}>
            <Text variant="bodyMedium">Name: {user?.name}</Text>
          </View>
          <View style={styles.profileRow}>
            <Text variant="bodyMedium">Email: {user?.email}</Text>
          </View>
          <View style={styles.profileRow}>
            <Text variant="bodyMedium">Role: {user?.role?.toUpperCase()}</Text>
          </View>
        </Card.Content>
      </Card>

      {isAdmin && (
        <>
          <Card style={styles.card}>
            <Card.Title title="Alert Thresholds" />
            <Card.Content>
              <View style={styles.settingRow}>
                <Text variant="bodyMedium">Theft Detection</Text>
                <Switch
                  value={settings.alertThresholds?.theft?.enabled}
                  onValueChange={(value) => {
                    setSettings({
                      ...settings,
                      alertThresholds: {
                        ...settings.alertThresholds,
                        theft: {
                          ...settings.alertThresholds.theft,
                          enabled: value,
                        },
                      },
                    });
                  }}
                />
              </View>
              <TextInput
                label="Confidence Threshold"
                value={String(settings.alertThresholds?.theft?.confidence || 75)}
                onChangeText={(text) => {
                  setSettings({
                    ...settings,
                    alertThresholds: {
                      ...settings.alertThresholds,
                      theft: {
                        ...settings.alertThresholds.theft,
                        confidence: parseInt(text) || 75,
                      },
                    },
                  });
                }}
                mode="outlined"
                keyboardType="numeric"
                style={styles.input}
              />
            </Card.Content>
          </Card>

          <Card style={styles.card}>
            <Card.Title title="Notification Preferences" />
            <Card.Content>
              <View style={styles.settingRow}>
                <Text variant="bodyMedium">Email Notifications</Text>
                <Switch
                  value={settings.notificationPreferences?.email?.enabled}
                  onValueChange={(value) => {
                    setSettings({
                      ...settings,
                      notificationPreferences: {
                        ...settings.notificationPreferences,
                        email: {
                          ...settings.notificationPreferences.email,
                          enabled: value,
                        },
                      },
                    });
                  }}
                />
              </View>
              <View style={styles.settingRow}>
                <Text variant="bodyMedium">Push Notifications</Text>
                <Switch
                  value={settings.notificationPreferences?.push?.enabled}
                  onValueChange={(value) => {
                    setSettings({
                      ...settings,
                      notificationPreferences: {
                        ...settings.notificationPreferences,
                        push: {
                          ...settings.notificationPreferences.push,
                          enabled: value,
                        },
                      },
                    });
                  }}
                />
              </View>
            </Card.Content>
          </Card>

          {isAdmin && (
            <Button
              mode="contained"
              onPress={handleSave}
              style={styles.saveButton}
              loading={saving}
            >
              Save Settings
            </Button>
          )}
        </>
      )}

      <Card style={styles.card}>
        <Card.Title title="Account" />
        <Card.Content>
          <Button mode="outlined" onPress={logout} style={styles.logoutButton}>
            Logout
          </Button>
        </Card.Content>
      </Card>

      {isAdmin && (
        <Card style={styles.card}>
          <Card.Title title="Admin" />
          <Card.Content>
            <Button
              mode="outlined"
              onPress={() => navigation.navigate('UserManagement')}
              style={styles.adminButton}
            >
              User Management
            </Button>
            <Button
              mode="outlined"
              onPress={() => navigation.navigate('Billing')}
              style={styles.adminButton}
            >
              Billing
            </Button>
          </Card.Content>
        </Card>
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
  card: {
    margin: 16,
    marginTop: 0,
  },
  profileRow: {
    marginBottom: 16,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  input: {
    marginTop: 8,
  },
  saveButton: {
    margin: 16,
    marginTop: 0,
  },
  logoutButton: {
    marginTop: 8,
  },
  adminButton: {
    marginTop: 8,
  },
});

export default SettingsScreen;





