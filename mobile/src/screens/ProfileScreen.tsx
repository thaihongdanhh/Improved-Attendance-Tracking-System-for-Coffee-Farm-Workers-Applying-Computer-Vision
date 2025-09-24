import React from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
} from 'react-native';
import {
  Surface,
  Text,
  Avatar,
  List,
  Button,
  Divider,
} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useNavigation } from '@react-navigation/native';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { logout } from '../store/slices/authSlice';

export default function ProfileScreen() {
  const navigation = useNavigation<any>();
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state.auth.user);

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <ScrollView style={styles.container}>
      <Surface style={styles.header} elevation={1}>
        <Avatar.Text size={80} label={user?.name?.charAt(0) || 'U'} />
        <Text variant="headlineSmall" style={styles.name}>
          {user?.name || 'User'}
        </Text>
        <Text variant="bodyMedium" style={styles.role}>
          {user?.role || 'Role'}
        </Text>
      </Surface>

      <Surface style={styles.section} elevation={1}>
        <List.Item
          title="Account Settings"
          description="Manage your account preferences"
          left={(props) => <List.Icon {...props} icon="account-cog" />}
          right={(props) => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {}}
        />
        <Divider />
        <List.Item
          title="Notifications"
          description="Configure notification settings"
          left={(props) => <List.Icon {...props} icon="bell" />}
          right={(props) => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {}}
        />
        <Divider />
        <List.Item
          title="Language"
          description="English"
          left={(props) => <List.Icon {...props} icon="translate" />}
          right={(props) => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {}}
        />
      </Surface>

      <Surface style={styles.section} elevation={1}>
        <List.Item
          title="Help & Support"
          description="Get help with the app"
          left={(props) => <List.Icon {...props} icon="help-circle" />}
          right={(props) => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {}}
        />
        <Divider />
        <List.Item
          title="Privacy Policy"
          description="Read our privacy policy"
          left={(props) => <List.Icon {...props} icon="shield-lock" />}
          right={(props) => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {}}
        />
        <Divider />
        <List.Item
          title="About"
          description="Version 2.0.0"
          left={(props) => <List.Icon {...props} icon="information" />}
          onPress={() => {}}
        />
      </Surface>

      <Surface style={styles.section} elevation={1}>
        <List.Item
          title="Face Enrollment"
          description="Register faces for farmers"
          left={(props) => <List.Icon {...props} icon="face-recognition" />}
          right={(props) => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => navigation.navigate('FaceEnrollmentWelcome')}
        />
      </Surface>

      <View style={styles.logoutContainer}>
        <Button
          mode="contained"
          onPress={handleLogout}
          style={styles.logoutButton}
          contentStyle={styles.logoutButtonContent}
        >
          Logout
        </Button>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  header: {
    alignItems: 'center',
    padding: 30,
    backgroundColor: 'white',
  },
  name: {
    marginTop: 16,
    color: '#111827',
  },
  role: {
    color: '#6B7280',
    marginTop: 4,
  },
  section: {
    marginTop: 16,
    backgroundColor: 'white',
  },
  logoutContainer: {
    padding: 20,
    marginTop: 20,
  },
  logoutButton: {
    backgroundColor: '#EF4444',
  },
  logoutButtonContent: {
    paddingVertical: 8,
  },
});