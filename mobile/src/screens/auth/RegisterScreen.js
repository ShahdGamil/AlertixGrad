import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import {
  TextInput,
  Button,
  Text,
  Surface,
  ActivityIndicator,
} from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import { colors } from '../../theme/theme';
import Icon from 'react-native-vector-icons/MaterialIcons';

const RegisterScreen = ({ navigation }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState('viewer');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { register } = useAuth();

  const handleRegister = async () => {
    if (!name || !email || !password || !confirmPassword) {
      setError('Please fill in all fields');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    setError('');

    console.log('Registering with role:', role);
    const result = await register(name, email, password, role);

    if (!result.success) {
      setError(result.message);
      setLoading(false);
    }
  };

  const RoleCard = ({ roleType, icon, title, description, isSelected, onPress }) => (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.7}
      style={[
        styles.roleCard,
        isSelected && styles.roleCardSelected
      ]}
    >
      <Icon
        name={icon}
        size={32}
        color={isSelected ? colors.primary : colors.textSecondary}
        style={styles.roleIcon}
      />
      <Text variant="titleSmall" style={[
        styles.roleTitle,
        isSelected && styles.roleTitleSelected
      ]}>
        {title}
      </Text>
      <Text variant="bodySmall" style={[
        styles.roleDescription,
        isSelected && styles.roleDescriptionSelected
      ]}>
        {description}
      </Text>
    </TouchableOpacity>
  );

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Surface style={styles.surface}>
          <Text variant="headlineMedium" style={styles.title}>
            Create Account
          </Text>

          {error ? (
            <Text style={styles.error}>{error}</Text>
          ) : null}

          <TextInput
            label="Name"
            value={name}
            onChangeText={setName}
            mode="outlined"
            style={styles.input}
            disabled={loading}
          />

          <TextInput
            label="Email"
            value={email}
            onChangeText={setEmail}
            mode="outlined"
            keyboardType="email-address"
            autoCapitalize="none"
            style={styles.input}
            disabled={loading}
          />

          <TextInput
            label="Password"
            value={password}
            onChangeText={setPassword}
            mode="outlined"
            secureTextEntry
            style={styles.input}
            disabled={loading}
          />

          <TextInput
            label="Confirm Password"
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            mode="outlined"
            secureTextEntry
            style={styles.input}
            disabled={loading}
          />

          <Text variant="titleMedium" style={styles.roleSectionTitle}>
            Select Role
          </Text>

          <View style={styles.roleContainer}>
            <RoleCard
              roleType="admin"
              icon="shield"
              title="Admin"
              description="Full access to all features"
              isSelected={role === 'admin'}
              onPress={() => {
                console.log('Selected role: admin');
                setRole('admin');
              }}
            />
            <RoleCard
              roleType="operator"
              icon="videocam"
              title="Operator"
              description="Manage cameras and alerts"
              isSelected={role === 'operator'}
              onPress={() => {
                console.log('Selected role: operator');
                setRole('operator');
              }}
            />
            <RoleCard
              roleType="viewer"
              icon="person"
              title="Viewer"
              description="View only access"
              isSelected={role === 'viewer'}
              onPress={() => {
                console.log('Selected role: viewer');
                setRole('viewer');
              }}
            />
          </View>
          
          {/* Debug: Show selected role */}
          {__DEV__ && (
            <Text style={styles.debugText}>Selected Role: {role}</Text>
          )}

          <Button
            mode="contained"
            onPress={handleRegister}
            style={styles.button}
            disabled={loading}
          >
            {loading ? <ActivityIndicator color="#fff" /> : 'Create Account'}
          </Button>

          <Button
            mode="text"
            onPress={() => navigation.navigate('Login')}
            style={styles.linkButton}
            disabled={loading}
          >
            Already have an account? Login
          </Button>
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
    justifyContent: 'center',
    padding: 20,
  },
  surface: {
    padding: 24,
    borderRadius: 8,
    elevation: 4,
    backgroundColor: '#fff',
  },
  title: {
    textAlign: 'center',
    marginBottom: 32,
    fontWeight: 'bold',
    color: colors.primary,
  },
  input: {
    marginBottom: 16,
    backgroundColor: '#fff',
  },
  error: {
    color: colors.error,
    textAlign: 'center',
    marginBottom: 16,
  },
  roleSectionTitle: {
    marginTop: 8,
    marginBottom: 16,
    fontWeight: 'bold',
    color: colors.text,
  },
  roleContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24,
    gap: 12,
  },
  roleCard: {
    flex: 1,
    padding: 16,
    borderRadius: 8,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    alignItems: 'center',
    minHeight: 140,
    justifyContent: 'center',
  },
  roleCardSelected: {
    backgroundColor: '#E3F2FD', // Light blue background
    borderColor: colors.primary, // Blue border
    borderWidth: 2,
  },
  roleIcon: {
    marginBottom: 12,
  },
  roleTitle: {
    fontWeight: 'bold',
    marginBottom: 8,
    color: colors.text,
  },
  roleTitleSelected: {
    color: colors.primary,
  },
  roleDescription: {
    textAlign: 'center',
    color: colors.textSecondary,
    fontSize: 12,
  },
  roleDescriptionSelected: {
    color: colors.text,
  },
  button: {
    marginTop: 8,
    paddingVertical: 4,
  },
  linkButton: {
    marginTop: 16,
  },
  debugText: {
    marginTop: 8,
    color: colors.textSecondary,
    fontSize: 12,
    textAlign: 'center',
  },
});

export default RegisterScreen;
