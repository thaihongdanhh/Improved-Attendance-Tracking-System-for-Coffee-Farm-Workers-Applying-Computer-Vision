import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import {
  Surface,
  Text,
  TextInput,
  Button,
  RadioButton,
  HelperText,
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useCreateFarmerMutation } from '../services';
import { format } from 'date-fns';
import { testCreateFarmer } from '../utils/testCreateFarmer';

export default function AddFarmerScreen() {
  const navigation = useNavigation<any>();
  const [createFarmer, { isLoading }] = useCreateFarmerMutation();

  const [formData, setFormData] = useState({
    farmer_code: '',
    full_name: '',
    phone: '',
    date_of_birth: '',
    gender: 'male',
    address: '',
    farm_id: 'default_farm',
  });

  const [errors, setErrors] = useState<any>({});

  const validateForm = () => {
    const newErrors: any = {};

    if (!formData.farmer_code.trim()) {
      newErrors.farmer_code = 'Farmer code is required';
    }

    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
    }

    // Phone is optional, validate only if provided
    if (formData.phone && formData.phone.trim() && !/^[0-9]{10,15}$/.test(formData.phone)) {
      newErrors.phone = 'Invalid phone number (10-15 digits)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    try {
      console.log('Submitting farmer data:', formData);
      
      // Clean up data before sending
      const dataToSend: any = {
        farmer_code: formData.farmer_code,
        full_name: formData.full_name,
        phone: formData.phone || undefined,
        farm_id: formData.farm_id,
        gender: formData.gender,
        address: formData.address || undefined,
      };
      
      // Only include date_of_birth if it has a value and format it properly
      if (formData.date_of_birth && formData.date_of_birth.length === 8) {
        // Convert YYYYDDMM to YYYY-MM-DD (assuming input is YYYYDDMM)
        const year = formData.date_of_birth.substring(0, 4);
        const day = formData.date_of_birth.substring(4, 6);
        const month = formData.date_of_birth.substring(6, 8);
        
        // Validate date parts
        const monthNum = parseInt(month);
        const dayNum = parseInt(day);
        
        if (monthNum >= 1 && monthNum <= 12 && dayNum >= 1 && dayNum <= 31) {
          dataToSend.date_of_birth = `${year}-${month}-${day}`;
        } else {
          // Try YYYYMMDD format instead
          const altMonth = formData.date_of_birth.substring(4, 6);
          const altDay = formData.date_of_birth.substring(6, 8);
          const altMonthNum = parseInt(altMonth);
          const altDayNum = parseInt(altDay);
          
          if (altMonthNum >= 1 && altMonthNum <= 12 && altDayNum >= 1 && altDayNum <= 31) {
            dataToSend.date_of_birth = `${year}-${altMonth}-${altDay}`;
          }
        }
      }
      
      const result = await createFarmer(dataToSend).unwrap();
      
      console.log('Farmer created successfully:', result);

      // Navigate to face enrollment for the new farmer
      navigation.navigate('FaceEnrollment', {
        farmerId: result.id,
        farmerName: result.full_name,
      });
    } catch (error: any) {
      console.error('Failed to create farmer:', error);
      
      // Show alert with error message
      let errorMessage = 'Failed to create farmer';
      if (error.data?.detail) {
        errorMessage = error.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      Alert.alert('Error', errorMessage);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors((prev: any) => ({ ...prev, [field]: null }));
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Surface style={styles.form} elevation={2}>
          <Text variant="headlineSmall" style={styles.title}>
            New Farmer Registration
          </Text>
          <Text variant="bodyMedium" style={styles.subtitle}>
            Enter farmer details to get started
          </Text>

          <TextInput
            label="Farmer Code *"
            value={formData.farmer_code}
            onChangeText={(text) => handleInputChange('farmer_code', text)}
            style={styles.input}
            mode="outlined"
            error={!!errors.farmer_code}
          />
          <HelperText type="error" visible={!!errors.farmer_code}>
            {errors.farmer_code}
          </HelperText>

          <TextInput
            label="Full Name *"
            value={formData.full_name}
            onChangeText={(text) => handleInputChange('full_name', text)}
            style={styles.input}
            mode="outlined"
            error={!!errors.full_name}
          />
          <HelperText type="error" visible={!!errors.full_name}>
            {errors.full_name}
          </HelperText>

          <TextInput
            label="Phone Number"
            value={formData.phone}
            onChangeText={(text) => handleInputChange('phone', text)}
            style={styles.input}
            mode="outlined"
            keyboardType="phone-pad"
            error={!!errors.phone}
          />
          <HelperText type="error" visible={!!errors.phone}>
            {errors.phone}
          </HelperText>

          <TextInput
            label="Date of Birth"
            value={formData.date_of_birth}
            onChangeText={(text) => handleInputChange('date_of_birth', text)}
            style={styles.input}
            mode="outlined"
            placeholder="YYYY-MM-DD"
          />

          <Text variant="labelLarge" style={styles.label}>
            Gender
          </Text>
          <RadioButton.Group
            value={formData.gender}
            onValueChange={(value) => handleInputChange('gender', value)}
          >
            <View style={styles.radioRow}>
              <RadioButton.Item label="Male" value="male" />
              <RadioButton.Item label="Female" value="female" />
              <RadioButton.Item label="Other" value="other" />
            </View>
          </RadioButton.Group>

          <TextInput
            label="Address"
            value={formData.address}
            onChangeText={(text) => handleInputChange('address', text)}
            style={styles.input}
            mode="outlined"
            multiline
            numberOfLines={3}
          />

          <View style={styles.notice}>
            <Text variant="bodySmall" style={styles.noticeText}>
              After registration, you'll be prompted to enroll the farmer's face for quick check-ins
            </Text>
          </View>
          
          <Button
            mode="text"
            onPress={async () => {
              try {
                const result = await testCreateFarmer();
                Alert.alert('Test Success', 'Direct API call worked!');
              } catch (error) {
                Alert.alert('Test Failed', 'Check console for details');
              }
            }}
          >
            Test Direct API
          </Button>
        </Surface>

        <View style={styles.actions}>
          <Button
            mode="outlined"
            onPress={() => navigation.goBack()}
            style={styles.cancelButton}
          >
            Cancel
          </Button>
          <Button
            mode="contained"
            onPress={handleSubmit}
            loading={isLoading}
            disabled={isLoading}
            style={styles.submitButton}
            contentStyle={styles.submitButtonContent}
          >
            Register & Continue
          </Button>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  scrollContent: {
    padding: 16,
  },
  form: {
    padding: 24,
    borderRadius: 12,
    backgroundColor: 'white',
  },
  title: {
    color: '#111827',
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitle: {
    color: '#6B7280',
    marginBottom: 24,
  },
  input: {
    marginBottom: 4,
  },
  label: {
    marginTop: 16,
    marginBottom: 8,
    color: '#374151',
  },
  radioRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  notice: {
    marginTop: 24,
    padding: 16,
    backgroundColor: '#F0FDF4',
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#10B981',
  },
  noticeText: {
    color: '#065F46',
  },
  actions: {
    flexDirection: 'row',
    marginTop: 20,
    gap: 12,
  },
  cancelButton: {
    flex: 1,
  },
  submitButton: {
    flex: 2,
  },
  submitButtonContent: {
    paddingVertical: 8,
  },
});