import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {
  TextInput,
  Button,
  Text,
  Surface,
  ActivityIndicator,
  RadioButton,
} from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import api from '../../config/api';
import { colors } from '../../theme/theme';
import Icon from 'react-native-vector-icons/MaterialIcons';

const AddUserScreen = ({ navigation, route }) => {
  console.log('AddUserScreen rendered', { route: route?.params });
  const { user: currentUser } = useAuth();
  const editingUser = route?.params?.user;
  const isEditing = !!editingUser;

  const [name, setName] = useState(editingUser?.name || '');
  const [email, setEmail] = useState(editingUser?.email || '');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState(editingUser?.role || 'operator');
  const [isActive, setIsActive] = useState(editingUser?.isActive !== false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async () => {
    if (!name || !email) {
      setError('Please fill in all required fields');
      return;
    }

    if (!isEditing && (!password || !confirmPassword)) {
      setError('Password is required for new users');
      return;
    }

    if (!isEditing && password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!isEditing && password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    setError('');

    try {
      if (isEditing) {
        // Update existing user
        const updateData = { name, email, role, isActive };
        if (password) {
          updateData.password = password;
        }
        await api.put(`/users/${editingUser._id}`, updateData);
      } else {
        // Create new user
        await api.post('/users', {
          name,
          email,
          password,
          role,
          isActive,
        });
      }
      navigation.goBack();
    } catch (error) {
      console.error('Save error:', error);
      setError(
        error.response?.data?.message ||
        (isEditing ? 'Failed to update user' : 'Failed to create user')
      );
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Surface style={styles.surface}>
          <View style={styles.header}>
            <Icon
              name={isEditing ? 'edit' : 'person-add'}
              size={32}
              color={colors.primary}
            />
            <Text variant="headlineMedium" style={styles.title}>
              {isEditing ? 'Edit User' : 'Add User'}
            </Text>
          </View>

          {error ? (
            <Text style={styles.error}>{error}</Text>
          ) : null}

          <TextInput
            label="Name *"
            value={name}
            onChangeText={setName}
            mode="outlined"
            style={styles.input}
            disabled={loading}
            left={<TextInput.Icon icon="account" />}
          />

          <TextInput
            label="Email *"
            value={email}
            onChangeText={setEmail}
            mode="outlined"
            keyboardType="email-address"
            autoCapitalize="none"
            style={styles.input}
            disabled={loading}
            left={<TextInput.Icon icon="email" />}
          />

          <TextInput
            label={isEditing ? 'New Password (leave empty to keep current)' : 'Password *'}
            value={password}
            onChangeText={setPassword}
            mode="outlined"
            secureTextEntry
            style={styles.input}
            disabled={loading}
            left={<TextInput.Icon icon="lock" />}
          />

          {!isEditing && (
            <TextInput
              label="Confirm Password *"
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              mode="outlined"
              secureTextEntry
              style={styles.input}
              disabled={loading}
              left={<TextInput.Icon icon="lock-check" />}
            />
          )}

          <Text variant="titleMedium" style={styles.sectionTitle}>
            Select Role
          </Text>

          <View style={styles.roleContainer}>
            <View style={styles.roleOption}>
              <RadioButton
                value="admin"
                status={role === 'admin' ? 'checked' : 'unchecked'}
                onPress={() => setRole('admin')}
                color={colors.primary}
              />
              <View style={styles.roleInfo}>
                <View style={styles.roleHeader}>
                  <Icon name="shield" size={24} color={colors.primary} />
                  <Text variant="titleSmall" style={styles.roleName}>Admin</Text>
                </View>
                <Text variant="bodySmall" style={styles.roleDesc}>
                  Full access to all features
                </Text>
              </View>
            </View>

            <View style={styles.roleOption}>
              <RadioButton
                value="operator"
                status={role === 'operator' ? 'checked' : 'unchecked'}
                onPress={() => setRole('operator')}
                color={colors.primary}
              />
              <View style={styles.roleInfo}>
                <View style={styles.roleHeader}>
                  <Icon name="videocam" size={24} color={colors.warning} />
                  <Text variant="titleSmall" style={styles.roleName}>Operator</Text>
                </View>
                <Text variant="bodySmall" style={styles.roleDesc}>
                  View assigned cameras and alerts only
                </Text>
              </View>
            </View>
          </View>

          <View style={styles.activeContainer}>
            <Text variant="bodyLarge">Active Status</Text>
            <RadioButton
              value="active"
              status={isActive ? 'checked' : 'unchecked'}
              onPress={() => setIsActive(true)}
              color={colors.success}
            />
            <Text variant="bodyMedium" style={styles.activeLabel}>Active</Text>

            <RadioButton
              value="inactive"
              status={!isActive ? 'checked' : 'unchecked'}
              onPress={() => setIsActive(false)}
              color={colors.error}
            />
            <Text variant="bodyMedium" style={styles.activeLabel}>Inactive</Text>
          </View>

          <View style={styles.buttonRow}>
            <Button
              mode="outlined"
              onPress={() => navigation.goBack()}
              style={styles.cancelButton}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              mode="contained"
              onPress={handleSave}
              style={styles.saveButton}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                isEditing ? 'Update User' : 'Create User'
              )}
            </Button>
          </View>
        </Surface>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 20,
  },
  surface: {
    padding: 24,
    borderRadius: 8,
    elevation: 4,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    marginTop: 8,
    fontWeight: 'bold',
    color: colors.primary,
  },
  input: {
    marginBottom: 16,
  },
  error: {
    color: colors.error,
    textAlign: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    marginTop: 8,
    marginBottom: 16,
    fontWeight: 'bold',
  },
  roleContainer: {
    marginBottom: 24,
  },
  roleOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    marginBottom: 8,
    backgroundColor: colors.surface,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  roleInfo: {
    flex: 1,
    marginLeft: 12,
  },
  roleHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 4,
  },
  roleName: {
    fontWeight: 'bold',
  },
  roleDesc: {
    color: colors.textSecondary,
    marginLeft: 32,
  },
  activeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
    padding: 16,
    backgroundColor: colors.surface,
    borderRadius: 8,
  },
  activeLabel: {
    marginRight: 16,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 16,
    marginTop: 8,
  },
  cancelButton: {
    flex: 1,
  },
  saveButton: {
    flex: 1,
  },
});

export default AddUserScreen;

