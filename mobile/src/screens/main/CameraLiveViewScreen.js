import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  Dimensions,
} from 'react-native';
import {
  Surface,
  Text,
  Button,
  IconButton,
} from 'react-native-paper';
import { colors } from '../../theme/theme';
import Icon from 'react-native-vector-icons/MaterialIcons';

const { width, height } = Dimensions.get('window');

const CameraLiveViewScreen = ({ route, navigation }) => {
  const { cameraId } = route.params;
  const [fullscreen, setFullscreen] = useState(false);
  const [zoom, setZoom] = useState(1);

  // In a real app, you would use react-native-video or a WebView to display the stream
  // This is a placeholder for the live view

  return (
    <View style={styles.container}>
      <Surface style={styles.videoContainer}>
        <View style={styles.placeholder}>
          <Icon name="videocam" size={64} color={colors.textSecondary} />
          <Text variant="bodyMedium" style={styles.placeholderText}>
            Live Stream View
          </Text>
          <Text variant="bodySmall" style={styles.placeholderSubtext}>
            Camera ID: {cameraId}
          </Text>
        </View>
      </Surface>

      <View style={styles.controls}>
        <IconButton
          icon="zoom-in"
          size={24}
          onPress={() => setZoom(Math.min(zoom + 0.1, 2))}
        />
        <IconButton
          icon="zoom-out"
          size={24}
          onPress={() => setZoom(Math.max(zoom - 0.1, 1))}
        />
        <IconButton
          icon="fullscreen"
          size={24}
          onPress={() => setFullscreen(!fullscreen)}
        />
        <IconButton
          icon="camera-alt"
          size={24}
          onPress={() => {
            // Take snapshot
          }}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  videoContainer: {
    flex: 1,
    margin: 16,
    borderRadius: 8,
    overflow: 'hidden',
  },
  placeholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.surface,
  },
  placeholderText: {
    marginTop: 16,
    color: colors.textSecondary,
  },
  placeholderSubtext: {
    marginTop: 8,
    color: colors.textSecondary,
  },
  controls: {
    flexDirection: 'row',
    justifyContent: 'center',
    padding: 16,
    backgroundColor: colors.surface,
  },
});

export default CameraLiveViewScreen;





