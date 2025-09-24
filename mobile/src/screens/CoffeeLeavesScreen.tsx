import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Image,
  Alert,
} from 'react-native';
import {
  Surface,
  Text,
  Button,
  Card,
  Chip,
  ActivityIndicator,
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import * as ImagePicker from 'expo-image-picker';
import { useAnalyzeCoffeeLeavesMutation } from '../services/coffeeLeavesApi';

export default function CoffeeLeavesScreen() {
  const navigation = useNavigation<any>();
  const [selectedImages, setSelectedImages] = useState<string[]>([]);
  const [analyzeCoffeeLeaves, { isLoading }] = useAnalyzeCoffeeLeavesMutation();

  const selectImages = () => {
    Alert.alert(
      'Select Images',
      'Choose from where you want to select images',
      [
        { text: 'Camera', onPress: openCamera },
        { text: 'Gallery', onPress: openGallery },
        { text: 'Cancel', style: 'cancel' },
      ]
    );
  };

  const openCamera = async () => {
    const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    
    if (permissionResult.granted === false) {
      Alert.alert('Permission Required', 'You need to allow camera access to take photos');
      return;
    }
    
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
      allowsEditing: false,
    });
    
    if (!result.canceled && result.assets[0]) {
      setSelectedImages([result.assets[0].uri]);
    }
  };

  const openGallery = async () => {
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (permissionResult.granted === false) {
      Alert.alert('Permission Required', 'You need to allow gallery access to select photos');
      return;
    }
    
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
      allowsMultipleSelection: false,
    });
    
    if (!result.canceled && result.assets[0]) {
      setSelectedImages([result.assets[0].uri]);
    }
  };

  const removeImage = (index: number) => {
    setSelectedImages(selectedImages.filter((_, i) => i !== index));
  };

  const analyzeImages = async () => {
    if (selectedImages.length === 0) {
      Alert.alert('Error', 'Please select at least one image');
      return;
    }

    try {
      // For now, analyze only the first image since backend expects single file
      const formData = new FormData();
      formData.append('file', {
        uri: selectedImages[0],
        type: 'image/jpeg',
        name: 'coffee_leaves.jpg',
      } as any);
      
      // Add optional form fields
      formData.append('farm_id', 'default_farm');
      formData.append('field_id', 'default_field');
      formData.append('notes', '');

      const result = await analyzeCoffeeLeaves(formData).unwrap();
      
      // Navigate to results screen
      navigation.navigate('CoffeeLeavesResult', { analysisId: result.id });
    } catch (error: any) {
      console.error('Analysis error:', error);
      Alert.alert('Error', error.data?.detail || 'Failed to analyze image');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Surface style={styles.header} elevation={2}>
        <Text variant="titleLarge">Coffee Leaves Analysis</Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          Detect diseases in coffee leaves using AI
        </Text>
      </Surface>

      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.cardTitle}>
            Instructions
          </Text>
          <Text variant="bodyMedium" style={styles.instruction}>
            • Take close-up photos of affected leaves
          </Text>
          <Text variant="bodyMedium" style={styles.instruction}>
            • Include both healthy and diseased areas
          </Text>
          <Text variant="bodyMedium" style={styles.instruction}>
            • Ensure good lighting without shadows
          </Text>
          <Text variant="bodyMedium" style={styles.instruction}>
            • You can upload up to 5 images
          </Text>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.cardTitle}>
            Common Diseases We Detect
          </Text>
          <View style={styles.diseaseList}>
            <Chip style={styles.diseaseChip}>Leaf Rust</Chip>
            <Chip style={styles.diseaseChip}>Brown Spot</Chip>
            <Chip style={styles.diseaseChip}>Berry Disease</Chip>
            <Chip style={styles.diseaseChip}>Leaf Miner</Chip>
          </View>
        </Card.Content>
      </Card>

      {selectedImages.length > 0 && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={styles.cardTitle}>
              Selected Images ({selectedImages.length}/5)
            </Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {selectedImages.map((uri, index) => (
                <View key={index} style={styles.imageContainer}>
                  <Image source={{ uri }} style={styles.previewImage} />
                  <Chip
                    icon="close"
                    onPress={() => removeImage(index)}
                    style={styles.removeChip}
                  >
                    Remove
                  </Chip>
                </View>
              ))}
            </ScrollView>
          </Card.Content>
        </Card>
      )}

      <View style={styles.actions}>
        <Button
          mode="outlined"
          onPress={selectImages}
          disabled={selectedImages.length >= 5 || isLoading}
          icon="camera"
          style={styles.button}
        >
          {selectedImages.length > 0 ? 'Add More Images' : 'Select Images'}
        </Button>

        {selectedImages.length > 0 && (
          <Button
            mode="contained"
            onPress={analyzeImages}
            loading={isLoading}
            disabled={isLoading}
            icon="magnify"
            style={styles.button}
          >
            Analyze Coffee Leaves
          </Button>
        )}
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
    padding: 20,
    backgroundColor: 'white',
    marginBottom: 16,
  },
  subtitle: {
    color: '#6B7280',
    marginTop: 4,
  },
  card: {
    marginHorizontal: 16,
    marginBottom: 16,
  },
  cardTitle: {
    marginBottom: 12,
    color: '#374151',
  },
  instruction: {
    color: '#6B7280',
    marginBottom: 6,
  },
  diseaseList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  diseaseChip: {
    backgroundColor: '#DBEAFE',
  },
  imageContainer: {
    marginRight: 12,
    alignItems: 'center',
  },
  previewImage: {
    width: 120,
    height: 120,
    borderRadius: 8,
    marginBottom: 8,
  },
  removeChip: {
    backgroundColor: '#FEE2E2',
  },
  actions: {
    padding: 16,
  },
  button: {
    marginBottom: 12,
  },
});