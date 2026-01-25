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
  Divider,
} from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import api from '../../config/api';
import { colors } from '../../theme/theme';

const AlertDetailScreen = ({ route, navigation }) => {
  const { alertId } = route.params;
  const { user } = useAuth();
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [note, setNote] = useState('');
  const [addingNote, setAddingNote] = useState(false);

  useEffect(() => {
    loadAlert();
  }, []);

  const loadAlert = async () => {
    try {
      const response = await api.get(`/alerts/${alertId}`);
      setAlert(response.data.data.alert);
    } catch (error) {
      console.error('Alert load error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async () => {
    try {
      await api.post(`/alerts/${alertId}/acknowledge`);
      loadAlert();
    } catch (error) {
      console.error('Acknowledge error:', error);
    }
  };

  const handleClose = async () => {
    try {
      await api.post(`/alerts/${alertId}/close`);
      loadAlert();
    } catch (error) {
      console.error('Close error:', error);
    }
  };

  const handleAddNote = async () => {
    if (!note.trim()) return;

    try {
      await api.post(`/alerts/${alertId}/notes`, { note });
      setNote('');
      setAddingNote(false);
      loadAlert();
    } catch (error) {
      console.error('Add note error:', error);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (!alert) {
    return (
      <View style={styles.center}>
        <Text>Alert not found</Text>
      </View>
    );
  }

  const canModify = user?.role === 'admin' || user?.role === 'operator';

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Title title="Alert Details" />
        <Card.Content>
          <View style={styles.detailRow}>
            <Text variant="bodySmall" style={styles.label}>Type:</Text>
            <Chip>{alert.type}</Chip>
          </View>
          <View style={styles.detailRow}>
            <Text variant="bodySmall" style={styles.label}>Severity:</Text>
            <Chip
              style={{
                backgroundColor:
                  alert.severity === 'critical'
                    ? colors.error
                    : alert.severity === 'high'
                    ? colors.warning
                    : colors.info,
              }}
              textStyle={{ color: '#fff' }}
            >
              {alert.severity}
            </Chip>
          </View>
          <View style={styles.detailRow}>
            <Text variant="bodySmall" style={styles.label}>Status:</Text>
            <Chip
              style={{
                backgroundColor:
                  alert.status === 'open'
                    ? colors.error
                    : alert.status === 'acknowledged'
                    ? colors.warning
                    : colors.success,
              }}
              textStyle={{ color: '#fff' }}
            >
              {alert.status}
            </Chip>
          </View>
          <View style={styles.detailRow}>
            <Text variant="bodySmall" style={styles.label}>Camera:</Text>
            <Text variant="bodyMedium">{alert.camera?.name}</Text>
          </View>
          <View style={styles.detailRow}>
            <Text variant="bodySmall" style={styles.label}>Location:</Text>
            <Text variant="bodyMedium">{alert.camera?.location}</Text>
          </View>
          <View style={styles.detailRow}>
            <Text variant="bodySmall" style={styles.label}>Detected At:</Text>
            <Text variant="bodyMedium">
              {new Date(alert.detectedAt).toLocaleString()}
            </Text>
          </View>
          {alert.description && (
            <View style={styles.descriptionContainer}>
              <Text variant="bodySmall" style={styles.label}>Description:</Text>
              <Text variant="bodyMedium">{alert.description}</Text>
            </View>
          )}
        </Card.Content>
      </Card>

      {canModify && alert.status === 'open' && (
        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.buttonRow}>
              <Button mode="contained" onPress={handleAcknowledge}>
                Acknowledge
              </Button>
              <Button mode="outlined" onPress={handleClose}>
                Close
              </Button>
            </View>
          </Card.Content>
        </Card>
      )}

      <Card style={styles.card}>
        <Card.Title title="Notes" />
        <Card.Content>
          {alert.notes && alert.notes.length > 0 ? (
            alert.notes.map((noteItem, index) => (
              <View key={index} style={styles.noteItem}>
                <Text variant="bodySmall" style={styles.noteUser}>
                  {noteItem.user?.name || 'Unknown'} -{' '}
                  {new Date(noteItem.createdAt).toLocaleString()}
                </Text>
                <Text variant="bodyMedium">{noteItem.note}</Text>
                {index < alert.notes.length - 1 && <Divider style={styles.divider} />}
              </View>
            ))
          ) : (
            <Text variant="bodySmall" style={styles.emptyNotes}>
              No notes yet
            </Text>
          )}

          {canModify && (
            <>
              {addingNote ? (
                <View style={styles.addNoteContainer}>
                  <TextInput
                    label="Add Note"
                    value={note}
                    onChangeText={setNote}
                    mode="outlined"
                    multiline
                    style={styles.noteInput}
                  />
                  <View style={styles.noteButtons}>
                    <Button onPress={() => { setAddingNote(false); setNote(''); }}>
                      Cancel
                    </Button>
                    <Button mode="contained" onPress={handleAddNote}>
                      Add
                    </Button>
                  </View>
                </View>
              ) : (
                <Button
                  mode="outlined"
                  onPress={() => setAddingNote(true)}
                  style={styles.addNoteButton}
                >
                  Add Note
                </Button>
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
    marginTop: 0,
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
  descriptionContainer: {
    marginTop: 8,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    gap: 16,
  },
  noteItem: {
    marginBottom: 16,
  },
  noteUser: {
    color: colors.textSecondary,
    marginBottom: 4,
  },
  divider: {
    marginTop: 16,
  },
  emptyNotes: {
    color: colors.textSecondary,
    fontStyle: 'italic',
  },
  addNoteContainer: {
    marginTop: 16,
  },
  noteInput: {
    marginBottom: 8,
  },
  noteButtons: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 8,
  },
  addNoteButton: {
    marginTop: 16,
  },
});

export default AlertDetailScreen;





