import React from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Image,
} from 'react-native';
import {
  Surface,
  Text,
  Button,
  List,
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

export default function FaceEnrollmentWelcomeScreen() {
  const navigation = useNavigation<any>();

  const steps = [
    {
      icon: 'face-recognition',
      title: 'Front Face',
      description: 'Look straight at the camera',
    },
    {
      icon: 'rotate-left',
      title: 'Left Profile',
      description: 'Turn your head slightly to the left',
    },
    {
      icon: 'rotate-right',
      title: 'Right Profile',
      description: 'Turn your head slightly to the right',
    },
  ];

  const tips = [
    {
      icon: 'lightbulb',
      text: 'Ensure good lighting',
    },
    {
      icon: 'glasses',
      text: 'Remove glasses if possible',
    },
    {
      icon: 'account',
      text: 'Keep a neutral expression',
    },
    {
      icon: 'camera-off',
      text: 'Avoid backlight',
    },
  ];

  return (
    <ScrollView style={styles.container}>
      <Surface style={styles.header} elevation={2}>
        <View style={styles.iconContainer}>
          <Icon name="face-recognition" size={80} color="#10B981" />
        </View>
        <Text variant="headlineMedium" style={styles.title}>
          Face Enrollment
        </Text>
        <Text variant="bodyLarge" style={styles.subtitle}>
          Register your face for quick and secure check-ins
        </Text>
      </Surface>

      <Surface style={styles.section} elevation={1}>
        <Text variant="titleLarge" style={styles.sectionTitle}>
          How it works
        </Text>
        <Text variant="bodyMedium" style={styles.sectionDescription}>
          We'll capture your face from 3 different angles
        </Text>
        
        {steps.map((step, index) => (
          <View key={index} style={styles.stepItem}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>{index + 1}</Text>
            </View>
            <Icon name={step.icon} size={40} color="#10B981" />
            <View style={styles.stepContent}>
              <Text variant="titleMedium" style={styles.stepTitle}>
                {step.title}
              </Text>
              <Text variant="bodyMedium" style={styles.stepDescription}>
                {step.description}
              </Text>
            </View>
          </View>
        ))}
      </Surface>

      <Surface style={styles.section} elevation={1}>
        <Text variant="titleLarge" style={styles.sectionTitle}>
          Tips for best results
        </Text>
        <View style={styles.tipsGrid}>
          {tips.map((tip, index) => (
            <View key={index} style={styles.tipItem}>
              <Icon name={tip.icon} size={24} color="#6B7280" />
              <Text variant="bodySmall" style={styles.tipText}>
                {tip.text}
              </Text>
            </View>
          ))}
        </View>
      </Surface>

      <View style={styles.footer}>
        <Text variant="bodyMedium" style={styles.privacyText}>
          🔒 Your face data is encrypted and stored securely
        </Text>
        <Text variant="bodySmall" style={styles.privacySubtext}>
          We respect your privacy and never share your data
        </Text>
        
        <Button
          mode="contained"
          onPress={() => navigation.navigate('SelectFarmer')}
          style={styles.startButton}
          contentStyle={styles.startButtonContent}
          icon="arrow-right"
        >
          Get Started
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
    padding: 32,
    backgroundColor: 'white',
  },
  iconContainer: {
    marginBottom: 16,
  },
  title: {
    color: '#111827',
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitle: {
    color: '#6B7280',
    textAlign: 'center',
    paddingHorizontal: 20,
  },
  section: {
    margin: 16,
    padding: 24,
    borderRadius: 12,
    backgroundColor: 'white',
  },
  sectionTitle: {
    color: '#111827',
    fontWeight: '600',
    marginBottom: 8,
  },
  sectionDescription: {
    color: '#6B7280',
    marginBottom: 24,
  },
  stepItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
    paddingLeft: 8,
  },
  stepNumber: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#10B981',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  stepNumberText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
  },
  stepContent: {
    flex: 1,
    marginLeft: 16,
  },
  stepTitle: {
    color: '#111827',
    fontWeight: '600',
  },
  stepDescription: {
    color: '#6B7280',
    marginTop: 2,
  },
  tipsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  tipItem: {
    width: '50%',
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  tipText: {
    color: '#6B7280',
    marginLeft: 8,
    flex: 1,
  },
  footer: {
    padding: 24,
    alignItems: 'center',
  },
  privacyText: {
    color: '#374151',
    textAlign: 'center',
    marginBottom: 4,
  },
  privacySubtext: {
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 24,
  },
  startButton: {
    borderRadius: 12,
    elevation: 2,
  },
  startButtonContent: {
    paddingVertical: 8,
    paddingHorizontal: 24,
  },
});