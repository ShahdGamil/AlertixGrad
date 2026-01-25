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
  Button,
  FAB,
  Chip,
} from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import api from '../../config/api';
import { colors } from '../../theme/theme';
import Icon from 'react-native-vector-icons/MaterialIcons';

const ReportsScreen = ({ navigation }) => {
  const { user } = useAuth();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      const response = await api.get('/reports');
      setReports(response.data.data.reports);
    } catch (error) {
      console.error('Reports load error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadReports();
  };

  const handleDownload = async (reportId) => {
    try {
      // In a real app, you would download the file
      // For now, just show a message
      console.log('Download report:', reportId);
    } catch (error) {
      console.error('Download error:', error);
    }
  };

  const renderReport = ({ item }) => (
    <Card style={styles.card}>
      <Card.Content>
        <Text variant="titleMedium" style={styles.reportTitle}>
          {item.title}
        </Text>
        <View style={styles.reportInfo}>
          <Text variant="bodySmall" style={styles.reportDate}>
            {new Date(item.createdAt).toLocaleString()}
          </Text>
          <Chip
            style={[
              styles.statusChip,
              {
                backgroundColor:
                  item.status === 'completed'
                    ? colors.success
                    : item.status === 'generating'
                    ? colors.warning
                    : colors.error,
              },
            ]}
            textStyle={{ color: '#fff', fontSize: 10 }}
          >
            {item.status}
          </Chip>
        </View>
        <View style={styles.reportDetails}>
          <Text variant="bodySmall">
            Type: {item.type} | Format: {item.format?.toUpperCase()}
          </Text>
          {item.metadata?.totalRecords && (
            <Text variant="bodySmall">
              Records: {item.metadata.totalRecords}
            </Text>
          )}
        </View>
        {item.status === 'completed' && (
          <Button
            mode="outlined"
            icon="download"
            onPress={() => handleDownload(item._id)}
            style={styles.downloadButton}
          >
            Download
          </Button>
        )}
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
        data={reports}
        renderItem={renderReport}
        keyExtractor={(item) => item._id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text>No reports found</Text>
          </View>
        }
      />
      {(user?.role === 'admin' || user?.role === 'operator') && (
        <FAB
          icon="plus"
          style={styles.fab}
          onPress={() => {
            // Navigate to generate report screen
            navigation.navigate('GenerateReport');
          }}
        />
      )}
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
  reportTitle: {
    fontWeight: 'bold',
    marginBottom: 8,
  },
  reportInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  reportDate: {
    color: colors.textSecondary,
  },
  statusChip: {
    marginLeft: 8,
  },
  reportDetails: {
    marginTop: 8,
    gap: 4,
  },
  downloadButton: {
    marginTop: 16,
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

export default ReportsScreen;





