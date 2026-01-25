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
} from 'react-native-paper';
import api from '../../config/api';
import { colors } from '../../theme/theme';

const BillingScreen = () => {
  const [billing, setBilling] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBilling();
  }, []);

  const loadBilling = async () => {
    try {
      const response = await api.get('/billing');
      setBilling(response.data.data.billingInfo);
    } catch (error) {
      console.error('Billing load error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (!billing) {
    return (
      <View style={styles.center}>
        <Text>Billing information not available</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Title title="Current Plan" />
        <Card.Content>
          <View style={styles.planRow}>
            <Text variant="headlineSmall" style={styles.planName}>
              {billing.plan}
            </Text>
            <Chip
              style={[
                styles.statusChip,
                { backgroundColor: billing.status === 'active' ? colors.success : colors.error },
              ]}
              textStyle={{ color: '#fff' }}
            >
              {billing.status}
            </Chip>
          </View>
          <View style={styles.billingRow}>
            <Text variant="bodyMedium">Billing Cycle: {billing.billingCycle}</Text>
          </View>
          <View style={styles.billingRow}>
            <Text variant="bodyMedium">
              Next Billing Date: {new Date(billing.nextBillingDate).toLocaleDateString()}
            </Text>
          </View>
          <View style={styles.billingRow}>
            <Text variant="headlineMedium" style={styles.amount}>
              ${billing.amount} {billing.currency}
            </Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Usage" />
        <Card.Content>
          <View style={styles.usageRow}>
            <Text variant="bodyMedium">Cameras: {billing.usage?.cameras}</Text>
          </View>
          <View style={styles.usageRow}>
            <Text variant="bodyMedium">
              Storage: {billing.usage?.storage?.used} / {billing.usage?.storage?.total}{' '}
              {billing.usage?.storage?.unit}
            </Text>
          </View>
          <View style={styles.usageRow}>
            <Text variant="bodyMedium">
              Alerts (This Month): {billing.usage?.alerts?.thisMonth} / {billing.usage?.alerts?.limit}
            </Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Payment Method" />
        <Card.Content>
          <View style={styles.paymentRow}>
            <Text variant="bodyMedium">
              {billing.paymentMethod?.brand} •••• {billing.paymentMethod?.last4}
            </Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Invoices" />
        <Card.Content>
          {billing.invoices && billing.invoices.length > 0 ? (
            billing.invoices.map((invoice, index) => (
              <View key={index} style={styles.invoiceRow}>
                <View style={styles.invoiceInfo}>
                  <Text variant="bodyMedium">{invoice.id}</Text>
                  <Text variant="bodySmall" style={styles.invoiceDate}>
                    {new Date(invoice.date).toLocaleDateString()}
                  </Text>
                </View>
                <View style={styles.invoiceActions}>
                  <Text variant="bodyMedium" style={styles.invoiceAmount}>
                    ${invoice.amount}
                  </Text>
                  <Chip
                    style={[
                      styles.statusChip,
                      { backgroundColor: invoice.status === 'paid' ? colors.success : colors.warning },
                    ]}
                    textStyle={{ color: '#fff', fontSize: 10 }}
                  >
                    {invoice.status}
                  </Chip>
                  <Button
                    mode="outlined"
                    compact
                    onPress={() => {
                      // Download invoice
                    }}
                  >
                    Download
                  </Button>
                </View>
              </View>
            ))
          ) : (
            <Text variant="bodySmall">No invoices found</Text>
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
  planRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  planName: {
    fontWeight: 'bold',
  },
  statusChip: {
    marginLeft: 8,
  },
  billingRow: {
    marginBottom: 12,
  },
  amount: {
    fontWeight: 'bold',
    color: colors.primary,
    marginTop: 8,
  },
  usageRow: {
    marginBottom: 12,
  },
  paymentRow: {
    marginBottom: 8,
  },
  invoiceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  invoiceInfo: {
    flex: 1,
  },
  invoiceDate: {
    color: colors.textSecondary,
    marginTop: 4,
  },
  invoiceActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  invoiceAmount: {
    fontWeight: 'bold',
  },
});

export default BillingScreen;





