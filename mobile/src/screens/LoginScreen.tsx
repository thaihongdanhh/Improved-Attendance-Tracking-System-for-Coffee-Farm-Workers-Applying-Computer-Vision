import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Image,
} from 'react-native';
import {
  TextInput,
  Button,
  Text,
  Surface,
  HelperText,
} from 'react-native-paper';
import { useAppDispatch } from '../store/hooks';
import { login } from '../store/slices/authSlice';
import { useLoginMutation } from '../services';

export default function LoginScreen() {
  const dispatch = useAppDispatch();
  const [loginApi] = useLoginMutation();
  const [email, setEmail] = useState('admin@aicoffee.com');
  const [password, setPassword] = useState('admin123');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async () => {
    if (!email || !password) {
      setError('Please enter email and password');
      return;
    }

    setError('');

    try {
      const result = await loginApi({ 
        email, 
        password 
      }).unwrap();
      
      dispatch(
        login({
          user: result.user,
          token: result.access_token,
        })
      );
    } catch (err: any) {
      setError(err.data?.detail || 'Login failed');
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <Surface style={styles.surface} elevation={2}>
          <View style={styles.logoContainer}>
            <Image
              source={require('../../assets/logo.jpg')}
              style={styles.logo}
              resizeMode="contain"
            />
          </View>

          <Text variant="headlineMedium" style={styles.title}>
            AI Face Coffee Farm
          </Text>
          <Text variant="bodyMedium" style={styles.subtitle}>
            Face Recognition Attendance System
          </Text>

          <TextInput
            label="Email"
            value={email}
            onChangeText={setEmail}
            style={styles.input}
            mode="outlined"
            autoCapitalize="none"
            keyboardType="email-address"
            left={<TextInput.Icon icon="email" />}
          />

          <TextInput
            label="Password"
            value={password}
            onChangeText={setPassword}
            style={styles.input}
            mode="outlined"
            secureTextEntry={!showPassword}
            left={<TextInput.Icon icon="lock" />}
            right={
              <TextInput.Icon
                icon={showPassword ? 'eye-off' : 'eye'}
                onPress={() => setShowPassword(!showPassword)}
              />
            }
          />

          <HelperText type="error" visible={!!error}>
            {error}
          </HelperText>

          <Button
            mode="contained"
            onPress={handleLogin}
            style={styles.button}
          >
            Login
          </Button>

        </Surface>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  surface: {
    padding: 30,
    borderRadius: 12,
    backgroundColor: 'white',
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  logo: {
    width: 100,
    height: 100,
  },
  title: {
    textAlign: 'center',
    marginBottom: 8,
    color: '#111827',
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 30,
    color: '#6B7280',
  },
  input: {
    marginBottom: 12,
  },
  button: {
    marginTop: 16,
    paddingVertical: 8,
  },
});