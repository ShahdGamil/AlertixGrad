import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Alert,
  Image,
  Modal,
  TouchableOpacity,
} from 'react-native';
import {
  Surface,
  Text,
  Card,
  ActivityIndicator,
  Chip,
  Button,
  IconButton,
} from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import api from '../../config/api';
import { colors } from '../../theme/theme';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { launchImageLibrary, launchCamera } from 'react-native-image-picker';

const DashboardScreen = ({ navigation }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [detectionResult, setDetectionResult] = useState(null);
  const [showResultModal, setShowResultModal] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [stats, setStats] = useState({
    activeCameras: 0,
    totalCameras: 0,
    openAlerts: 0,
    recentAlerts: [],
    systemStatus: 'operational',
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [camerasRes, alertsRes] = await Promise.all([
        api.get('/cameras?limit=100'),
        api.get('/alerts?status=open&limit=5'),
      ]);

      const cameras = camerasRes.data.data.cameras;
      const alerts = alertsRes.data.data.alerts;

      setStats({
        activeCameras: cameras.filter(c => c.status === 'online').length,
        totalCameras: cameras.length,
        openAlerts: alertsRes.data.data.stats.open,
        recentAlerts: alerts,
        systemStatus: 'operational',
      });
    } catch (error) {
      console.error('Dashboard load error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboardData();
  };

  const handleUploadImage = () => {
    Alert.alert(
      'Upload Image',
      'Choose image source for theft detection',
      [
        {
          text: 'Camera',
          onPress: () => pickImage('camera'),
        },
        {
          text: 'Gallery',
          onPress: () => pickImage('gallery'),
        },
        {
          text: 'Cancel',
          style: 'cancel',
        },
      ]
    );
  };

  const pickImage = async (source) => {
    const options = {
      mediaType: 'photo',
      quality: 0.8,
      maxWidth: 1280,
      maxHeight: 1280,
    };

    try {
      let result;
      if (source === 'camera') {
        result = await launchCamera(options);
      } else {
        result = await launchImageLibrary(options);
      }

      if (result.didCancel) {
        return;
      }

      if (result.errorCode) {
        Alert.alert('Error', result.errorMessage || 'Failed to pick image');
        return;
      }

      if (result.assets && result.assets[0]) {
        const image = result.assets[0];
        setSelectedImage(image);
        await analyzeImage(image);
      }
    } catch (error) {
      console.error('Image picker error:', error);
      Alert.alert('Error', 'Failed to pick image');
    }
  };

  const analyzeImage = async (image) => {
    setUploading(true);
    setDetectionResult(null);

    try {
      const formData = new FormData();
      formData.append('image', {
        uri: image.uri,
        type: image.type || 'image/jpeg',
        name: image.fileName || 'upload.jpg',
      });

      // Send to backend which forwards to AI service
      const response = await api.post('/ai/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 seconds for AI processing
      });

      const result = response.data.data;
      setDetectionResult(result);
      setShowResultModal(true);

      // If theft detected, it's automatically saved to snapshots by backend
      if (result.detections?.some(d => d.class === 'theft')) {
        Alert.alert(
          'Theft Detected!',
          'The image has been saved to Snapshots and an alert has been created.',
          [{ text: 'View Snapshots', onPress: () => navigation.navigate('Snapshots') }]
        );
      }
    } catch (error) {
      console.error('Detection error:', error);
      Alert.alert(
        'Detection Failed',
        error.response?.data?.message || 'Failed to analyze image. Please try again.'
      );
    } finally {
      setUploading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return colors.error;
      case 'high': return colors.warning;
      case 'medium': return '#FF9800';
      default: return colors.info;
    }
  };

  const getDetectionColor = (className) => {
    switch (className) {
      case 'theft': return colors.error;
      case 'product_picked': return colors.warning;
      case 'customer_bagpack': return '#FF9800';
      case 'normal': return colors.success;
      default: return colors.info;
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
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text variant="headlineSmall" style={styles.welcomeText}>
          Welcome, {user?.name}
        </Text>
        <Text variant="bodyMedium" style={styles.roleText}>
          {user?.role?.toUpperCase()}
        </Text>
      </View>

      {/* Upload Image Card */}
      <Card style={[styles.card, styles.uploadCard]}>
        <Card.Content>
          <View style={styles.uploadHeader}>
            <Icon name="cloud-upload" size={32} color={colors.primary} />
            <Text variant="titleMedium" style={styles.uploadTitle}>
              Test Theft Detection
            </Text>
          </View>
          <Text variant="bodySmall" style={styles.uploadDesc}>
            Upload an image to test the AI theft detection system
          </Text>
          <Button
            mode="contained"
            onPress={handleUploadImage}
            loading={uploading}
            disabled={uploading}
            icon="camera"
            style={styles.uploadButton}
          >
            {uploading ? 'Analyzing...' : 'Upload Image'}
          </Button>
        </Card.Content>
      </Card>

      <View style={styles.statsRow}>
        <Card style={styles.statCard}>
          <Card.Content>
            <Icon name="videocam" size={32} color={colors.primary} />
            <Text variant="headlineMedium" style={styles.statValue}>
              {stats.activeCameras}/{stats.totalCameras}
            </Text>
            <Text variant="bodySmall" style={styles.statLabel}>
              Active Cameras
            </Text>
          </Card.Content>
        </Card>

        <Card style={styles.statCard}>
          <Card.Content>
            <Icon name="notifications" size={32} color={colors.error} />
            <Text variant="headlineMedium" style={styles.statValue}>
              {stats.openAlerts}
            </Text>
            <Text variant="bodySmall" style={styles.statLabel}>
              Open Alerts
            </Text>
          </Card.Content>
        </Card>
      </View>

      <Card style={styles.card} onPress={() => navigation.navigate('Alerts')}>
        <Card.Title title="Recent Alerts" />
        <Card.Content>
          {stats.recentAlerts.length === 0 ? (
            <Text>No recent alerts</Text>
          ) : (
            stats.recentAlerts.map((alert) => (
              <View key={alert._id} style={styles.alertItem}>
                <View style={styles.alertInfo}>
                  <Text variant="bodyMedium" style={styles.alertType}>
                    {alert.type?.toUpperCase()}
                  </Text>
                  <Text variant="bodySmall" style={styles.alertCamera}>
                    {alert.camera?.name || 'Unknown'}
                  </Text>
                </View>
                <Chip
                  style={[
                    styles.severityChip,
                    { backgroundColor: getSeverityColor(alert.severity) },
                  ]}
                  textStyle={{ color: '#fff', fontSize: 10 }}
                >
                  {alert.severity}
                </Chip>
              </View>
            ))
          )}
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="System Status" />
        <Card.Content>
          <View style={styles.statusRow}>
            <Icon name="check-circle" size={24} color={colors.success} />
            <Text variant="bodyMedium" style={styles.statusText}>
              All systems operational
            </Text>
          </View>
        </Card.Content>
      </Card>

      {/* Detection Result Modal */}
      <Modal
        visible={showResultModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowResultModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text variant="titleLarge" style={styles.modalTitle}>
                Detection Results
              </Text>
              <IconButton
                icon="close"
                size={24}
                onPress={() => setShowResultModal(false)}
              />
            </View>

            {selectedImage && (
              <Image
                source={{ uri: selectedImage.uri }}
                style={styles.resultImage}
                resizeMode="contain"
              />
            )}

            {detectionResult && (
              <View style={styles.detectionsContainer}>
                <Text variant="titleMedium" style={styles.detectionsTitle}>
                  Detections: {detectionResult.detections?.length || 0}
                </Text>

                {detectionResult.detections?.length === 0 ? (
                  <View style={styles.noDetection}>
                    <Icon name="check-circle" size={48} color={colors.success} />
                    <Text variant="bodyLarge" style={styles.noDetectionText}>
                      No suspicious activity detected
                    </Text>
                  </View>
                ) : (
                  detectionResult.detections?.map((detection, index) => (
                    <View key={index} style={styles.detectionItem}>
                      <View style={styles.detectionInfo}>
                        <Icon
                          name={detection.class === 'theft' ? 'warning' : 'info'}
                          size={24}
                          color={getDetectionColor(detection.class)}
                        />
                        <View style={styles.detectionText}>
                          <Text variant="bodyMedium" style={styles.detectionClass}>
                            {detection.class?.replace('_', ' ').toUpperCase()}
                          </Text>
                          <Text variant="bodySmall" style={styles.detectionConfidence}>
                            Confidence: {(detection.confidence * 100).toFixed(1)}%
                          </Text>
                        </View>
                      </View>
                      <Chip
                        style={[
                          styles.detectionChip,
                          { backgroundColor: getDetectionColor(detection.class) },
                        ]}
                        textStyle={{ color: '#fff', fontSize: 10 }}
                      >
                        {detection.class === 'theft' ? 'ALERT' : 'INFO'}
                      </Chip>
                    </View>
                  ))
                )}
              </View>
            )}

            <Button
              mode="contained"
              onPress={() => setShowResultModal(false)}
              style={styles.closeButton}
            >
              Close
            </Button>
          </View>
        </View>
      </Modal>
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
    padding: 20,
    backgroundColor: colors.surface,
  },
  welcomeText: {
    fontWeight: 'bold',
  },
  roleText: {
    color: colors.textSecondary,
    marginTop: 4,
  },
  uploadCard: {
    margin: 16,
    backgroundColor: colors.surface,
    borderWidth: 2,
    borderColor: colors.primary,
    borderStyle: 'dashed',
  },
  uploadHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  uploadTitle: {
    marginLeft: 12,
    fontWeight: 'bold',
    color: colors.primary,
  },
  uploadDesc: {
    color: colors.textSecondary,
    marginBottom: 16,
  },
  uploadButton: {
    marginTop: 8,
  },
  statsRow: {
    flexDirection: 'row',
    padding: 16,
    paddingTop: 0,
    gap: 16,
  },
  statCard: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    fontWeight: 'bold',
    marginTop: 8,
    textAlign: 'center',
  },
  statLabel: {
    color: colors.textSecondary,
    marginTop: 4,
    textAlign: 'center',
  },
  card: {
    margin: 16,
    marginTop: 0,
  },
  alertItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
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
  severityChip: {
    marginLeft: 8,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  statusText: {
    marginLeft: 8,
  },
  // Modal Styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    width: '90%',
    maxHeight: '80%',
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTitle: {
    fontWeight: 'bold',
  },
  resultImage: {
    width: '100%',
    height: 200,
    borderRadius: 8,
    marginBottom: 16,
  },
  detectionsContainer: {
    marginBottom: 16,
  },
  detectionsTitle: {
    fontWeight: 'bold',
    marginBottom: 12,
  },
  noDetection: {
    alignItems: 'center',
    padding: 24,
  },
  noDetectionText: {
    marginTop: 12,
    color: colors.success,
  },
  detectionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    backgroundColor: colors.background,
    borderRadius: 8,
    marginBottom: 8,
  },
  detectionInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  detectionText: {
    marginLeft: 12,
  },
  detectionClass: {
    fontWeight: 'bold',
  },
  detectionConfidence: {
    color: colors.textSecondary,
  },
  detectionChip: {
    marginLeft: 8,
  },
  closeButton: {
    marginTop: 8,
  },
});

export default DashboardScreen;
