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
  Chip,
  TextInput,
} from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import api from '../../config/api';
import { colors } from '../../theme/theme';
import Icon from 'react-native-vector-icons/MaterialIcons';

const CameraDetailScreen = ({ route, navigation }) => {
  const { cameraId } = route.params;
  const { user } = useAuth();
  const [camera, setCamera] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    if (cameraId) {
      loadCamera();
    } else {
      setCamera({});
      setFormData({});
      setEditing(true);
      setLoading(false);
    }
  }, [cameraId]);

  const loadCamera = async () => {
    try {
      const response = await api.get(`/cameras/${cameraId}`);
      setCamera(response.data.data.camera);
      setFormData(response.data.data.camera);
    } catch (error) {
      console.error('Camera load error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      if (cameraId) {
        await api.put(`/cameras/${cameraId}`, formData);
      } else {
        await api.post('/cameras', formData);
      }
      navigation.goBack();
    } catch (error) {
      console.error('Save error:', error);
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
      <Card style={styles.card}>
        <Card.Title title="Camera Information" />
        <Card.Content>
          {editing ? (
            <>
              <TextInput
                label="Name"
                value={formData.name || ''}
                onChangeText={(text) => setFormData({ ...formData, name: text })}
                mode="outlined"
                style={styles.input}
              />
              <TextInput
                label="Location"
                value={formData.location || ''}
                onChangeText={(text) => setFormData({ ...formData, location: text })}
                mode="outlined"
                style={styles.input}
              />
              <TextInput
                label="IP Address"
                value={formData.ipAddress || ''}
                onChangeText={(text) => setFormData({ ...formData, ipAddress: text })}
                mode="outlined"
                style={styles.input}
                keyboardType="numeric"
              />
              <TextInput
                label="Stream URL"
                value={formData.streamUrl || ''}
                onChangeText={(text) => setFormData({ ...formData, streamUrl: text })}
                mode="outlined"
                style={styles.input}
              />
              <View style={styles.buttonRow}>
                <Button mode="outlined" onPress={() => setEditing(false)}>
                  Cancel
                </Button>
                <Button mode="contained" onPress={handleSave}>
                  Save
                </Button>
              </View>
            </>
          ) : (
            <>
              <View style={styles.detailRow}>
                <Text variant="bodySmall" style={styles.label}>Name:</Text>
                <Text variant="bodyMedium">{camera?.name}</Text>
              </View>
              <View style={styles.detailRow}>
                <Text variant="bodySmall" style={styles.label}>Location:</Text>
                <Text variant="bodyMedium">{camera?.location}</Text>
              </View>
              <View style={styles.detailRow}>
                <Text variant="bodySmall" style={styles.label}>IP Address:</Text>
                <Text variant="bodyMedium">{camera?.ipAddress}</Text>
              </View>
              <View style={styles.detailRow}>
                <Text variant="bodySmall" style={styles.label}>Status:</Text>
                <Chip style={[styles.statusChip, { backgroundColor: camera?.status === 'online' ? colors.online : colors.offline }]}>
                  {camera?.status}
                </Chip>
              </View>
              {(user?.role === 'admin' || user?.role === 'operator') && (
                <View style={styles.buttonRow}>
                  <Button mode="outlined" onPress={() => setEditing(true)}>
                    Edit
                  </Button>
                  <Button
                    mode="contained"
                    onPress={() => navigation.navigate('CameraLiveView', { cameraId: camera._id })}
                  >
                    Live View
                  </Button>
                </View>
              )}
            </>
          )}
        </Card.Content>
      </Card>
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
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  label: {
    color: colors.textSecondary,
  },
  statusChip: {
    marginLeft: 8,
  },
  input: {
    marginBottom: 16,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
    gap: 16,
  },
});

export default CameraDetailScreen;





