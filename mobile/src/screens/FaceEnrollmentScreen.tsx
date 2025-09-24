import React, { useState, useRef } from 'react';
import {
  View,
  StyleSheet,
  Alert,
  Dimensions,
  ScrollView,
  Image,
} from 'react-native';
import {
  Surface,
  Text,
  Button,
  ProgressBar,
  Chip,
  IconButton,
  ActivityIndicator,
} from 'react-native-paper';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useRoute, useNavigation } from '@react-navigation/native';
import { useEnrollFaceMutation, useCheckFaceQualityMutation } from '../services';

const { width } = Dimensions.get('window');

const angles = ['front', 'left', 'right'] as const;
const angleInstructions = {
  front: 'Look straight at the camera',
  left: 'Turn your head slightly to the left',
  right: 'Turn your head slightly to the right'
};

const angleEmojis = {
  front: '😊',
  left: '👈',
  right: '👉'
};

// Display labels that match what user sees (selfie camera is mirrored)
// When user turns left, the saved image shows them turning right
const angleDisplayLabels = {
  front: 'FRONT',
  left: 'RIGHT',  // User turned left, but image shows right turn
  right: 'LEFT'   // User turned right, but image shows left turn
};

export default function FaceEnrollmentScreen() {
  const route = useRoute<any>();
  const navigation = useNavigation();
  const { farmerId, farmerName, isEnrolled } = route.params;
  
  const cameraRef = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [currentAngle, setCurrentAngle] = useState<typeof angles[number]>('front');
  const [capturedImages, setCapturedImages] = useState<{ [key: string]: string }>({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  
  const [enrollFace] = useEnrollFaceMutation();
  const [checkFaceQuality] = useCheckFaceQualityMutation();
  
  React.useEffect(() => {
    if (isEnrolled) {
      Alert.alert(
        'Face Already Enrolled',
        `${farmerName} already has face data enrolled. Do you want to update it with new photos?`,
        [
          {
            text: 'Cancel',
            onPress: () => navigation.goBack(),
            style: 'cancel'
          },
          {
            text: 'Update',
            onPress: () => console.log('User chose to update face enrollment')
          }
        ]
      );
    }
  }, [isEnrolled, farmerName, navigation]);

  const capture = async () => {
    if (!cameraRef.current) return;
    
    setIsProcessing(true);
    try {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.8,
        base64: true,  // Request base64 data
      });
      
      if (photo && photo.base64) {
        // Check face quality using JSON endpoint
        try {
          const qualityResult = await checkFaceQuality({
            image: `data:image/jpeg;base64,${photo.base64}`,
            expected_angle: currentAngle
          }).unwrap();
          
          if (!qualityResult.face_detected) {
            Alert.alert('No Face Detected', 'Please make sure your face is clearly visible in the frame.');
            setIsProcessing(false);
            return;
          }
          
          if (qualityResult.quality_score < 0.7) {
            const recommendations = qualityResult.recommendations?.join('\n') || 'Please improve image quality';
            const yaw = qualityResult.quality_details?.pose?.yaw || 0;
            Alert.alert(
              'Image Quality Too Low',
              `Quality Score: ${(qualityResult.quality_score * 100).toFixed(0)}%\nCurrent angle: ${yaw.toFixed(1)}°\n\n${recommendations}\n\nPlease try again.`,
              [{ text: 'OK', onPress: () => setIsProcessing(false) }]
            );
            return;
          }
          
          // Quality is good, save the image
          setCapturedImages(prev => ({ 
            ...prev, 
            [currentAngle]: `data:image/jpeg;base64,${photo.base64}` 
          }));
          
          // Auto advance to next angle
          const currentIndex = angles.indexOf(currentAngle);
          if (currentIndex < angles.length - 1) {
            setTimeout(() => {
              setCurrentAngle(angles[currentIndex + 1]);
              setIsProcessing(false);
            }, 500);
          } else {
            setShowPreview(true);
            setIsProcessing(false);
          }
        } catch (error: any) {
          console.error('Quality check failed:', error);
          Alert.alert('Error', 'Failed to check image quality. Please try again.');
          setIsProcessing(false);
        }
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to capture photo');
      setIsProcessing(false);
    }
  };

  const retakePhoto = (angle: string) => {
    const newImages = { ...capturedImages };
    delete newImages[angle];
    setCapturedImages(newImages);
    setCurrentAngle(angle as typeof angles[number]);
    setShowPreview(false);
  };

  const retakeAll = () => {
    setCapturedImages({});
    setCurrentAngle('front');
    setShowPreview(false);
  };

  const handleComplete = async () => {
    if (Object.keys(capturedImages).length < 3) {
      Alert.alert('Error', 'Please capture all three angles');
      return;
    }

    setIsProcessing(true);
    
    try {
      // Debug: Test direct API call first
      console.log('Testing direct API connection...');
      const testResponse = await fetch('http://kmou.n2nai.io:5200/health');
      const testData = await testResponse.json();
      console.log('Health check response:', testData);
      
      let enrollmentSuccess = true;
      
      // Prepare enrollment data in the format the API expects
      const enrollmentData = {
        farmer_id: farmerId,
        images: {
          front: capturedImages.front || null,
          left: capturedImages.left || null,
          right: capturedImages.right || null,
        }
      };
      
      console.log(`Enrolling face for farmer ${farmerId}...`);
      const result = await enrollFace(enrollmentData).unwrap();
      
      if (!result.success) {
        enrollmentSuccess = false;
        throw new Error(result.message);
      }
      
      if (enrollmentSuccess) {
        const message = result.was_update 
          ? 'Face data has been updated successfully!' 
          : 'Face enrollment completed successfully!';
        
        Alert.alert(
          '✅ Success',
          message,
          [
            {
              text: 'OK',
              onPress: () => navigation.goBack(),
            },
          ]
        );
      }
    } catch (error: any) {
      console.error('Enrollment error:', error);
      Alert.alert('❌ Error', error.data?.detail || error.message || 'Failed to enroll face');
    } finally {
      setIsProcessing(false);
    }
  };

  if (!permission) {
    return <View style={styles.container} />;
  }

  if (!permission.granted) {
    return (
      <View style={styles.centerContainer}>
        <Text variant="headlineSmall" style={styles.permissionTitle}>
          Camera Permission Required
        </Text>
        <Text variant="bodyMedium" style={styles.permissionText}>
          We need camera access to capture your face for enrollment
        </Text>
        <Button 
          mode="contained" 
          onPress={requestPermission}
          style={styles.permissionButton}
        >
          Grant Permission
        </Button>
      </View>
    );
  }

  const progress = Object.keys(capturedImages).length / 3;

  return (
    <View style={styles.container}>
      <Surface style={styles.header} elevation={2}>
        <Text variant="titleLarge" style={styles.headerTitle}>
          Face Enrollment
        </Text>
        <Text variant="bodyMedium" style={styles.headerSubtitle}>
          {farmerName}
        </Text>
        <ProgressBar progress={progress} style={styles.progressBar} />
        <View style={styles.angleChips}>
          {angles.map((angle) => (
            <View key={angle} style={styles.chipContainer}>
              <Chip
                mode={currentAngle === angle ? 'flat' : 'outlined'}
                selected={!!capturedImages[angle]}
                style={[
                  styles.chip,
                  currentAngle === angle && styles.activeChip,
                  capturedImages[angle] && styles.completedChip
                ]}
                textStyle={styles.chipText}
              >
                {angleEmojis[angle]} {angle}
              </Chip>
              {capturedImages[angle] && (
                <Text style={styles.checkMark}>✓</Text>
              )}
            </View>
          ))}
        </View>
      </Surface>

      {!showPreview ? (
        <>
          <View style={styles.cameraContainer}>
            <CameraView
              ref={cameraRef}
              style={styles.camera}
              facing="front"
            />
            <View style={styles.overlay}>
              <View style={styles.faceGuide}>
                <View style={styles.cornerTL} />
                <View style={styles.cornerTR} />
                <View style={styles.cornerBL} />
                <View style={styles.cornerBR} />
              </View>
              {currentAngle !== 'front' && (
                <View style={styles.arrowContainer}>
                  <Text style={styles.arrowEmoji}>
                    {angleEmojis[currentAngle]}
                  </Text>
                </View>
              )}
            </View>
          </View>

          <Surface style={styles.controls} elevation={2}>
            <Text variant="headlineSmall" style={styles.instruction}>
              {angleInstructions[currentAngle]}
            </Text>
            <Text variant="bodyMedium" style={styles.subInstruction}>
              Keep your face within the frame
            </Text>
            <Button
              mode="contained"
              onPress={capture}
              style={styles.captureButton}
              contentStyle={styles.captureButtonContent}
              icon="camera"
              disabled={isProcessing}
              loading={isProcessing}
            >
              {isProcessing ? 'Checking Quality...' : `Capture ${currentAngle}`}
            </Button>
          </Surface>
        </>
      ) : (
        <ScrollView contentContainerStyle={styles.reviewContainer}>
          <Surface style={styles.reviewHeader} elevation={1}>
            <Text variant="headlineSmall" style={styles.reviewTitle}>
              Review Your Photos
            </Text>
            <Text variant="bodyMedium" style={styles.reviewSubtitle}>
              Make sure your face is clearly visible in all photos
            </Text>
          </Surface>
          
          <View style={styles.imagesGrid}>
            {angles.map((angle) => (
              <Surface key={angle} style={styles.imageCard} elevation={2}>
                <Text variant="labelLarge" style={styles.angleLabel}>
                  {angle === 'left' ? '👉' : angle === 'right' ? '👈' : '😊'} {angleDisplayLabels[angle]}
                </Text>
                {capturedImages[angle] && (
                  <>
                    <Image
                      source={{ uri: capturedImages[angle] }}
                      style={styles.previewImage}
                      resizeMode="cover"
                    />
                    <IconButton
                      icon="camera-retake"
                      size={24}
                      style={styles.retakeButton}
                      onPress={() => retakePhoto(angle)}
                      mode="contained"
                    />
                  </>
                )}
              </Surface>
            ))}
          </View>

          <View style={styles.reviewActions}>
            <Button
              mode="outlined"
              onPress={retakeAll}
              style={styles.retakeAllButton}
            >
              Retake All
            </Button>
            <Button
              mode="contained"
              onPress={handleComplete}
              loading={isProcessing}
              disabled={isProcessing}
              style={styles.completeButton}
              contentStyle={styles.completeButtonContent}
            >
              Complete Enrollment
            </Button>
          </View>
        </ScrollView>
      )}

      {isProcessing && (
        <View style={styles.processingOverlay}>
          <Surface style={styles.processingCard} elevation={5}>
            <ActivityIndicator size="large" />
            <Text variant="bodyLarge" style={styles.processingText}>
              Enrolling face...
            </Text>
          </Surface>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  permissionTitle: {
    marginBottom: 16,
    color: '#111827',
  },
  permissionText: {
    marginBottom: 24,
    textAlign: 'center',
    color: '#6B7280',
  },
  permissionButton: {
    paddingHorizontal: 24,
  },
  header: {
    padding: 20,
    backgroundColor: 'white',
  },
  headerTitle: {
    color: '#111827',
    fontWeight: 'bold',
  },
  headerSubtitle: {
    color: '#6B7280',
    marginTop: 4,
  },
  progressBar: {
    marginTop: 16,
    marginBottom: 20,
    height: 8,
    borderRadius: 4,
  },
  angleChips: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  chipContainer: {
    position: 'relative',
  },
  chip: {
    backgroundColor: '#F3F4F6',
  },
  activeChip: {
    backgroundColor: '#DBEAFE',
  },
  completedChip: {
    backgroundColor: '#D1FAE5',
  },
  chipText: {
    fontSize: 12,
  },
  checkMark: {
    position: 'absolute',
    top: -8,
    right: -8,
    color: '#10B981',
    fontSize: 16,
    fontWeight: 'bold',
  },
  cameraContainer: {
    flex: 1,
    margin: 16,
    borderRadius: 16,
    overflow: 'hidden',
    elevation: 3,
  },
  camera: {
    flex: 1,
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  faceGuide: {
    width: width * 0.7,
    height: width * 0.85,
    position: 'relative',
  },
  cornerTL: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: 40,
    height: 40,
    borderTopWidth: 3,
    borderLeftWidth: 3,
    borderColor: '#10B981',
  },
  cornerTR: {
    position: 'absolute',
    top: 0,
    right: 0,
    width: 40,
    height: 40,
    borderTopWidth: 3,
    borderRightWidth: 3,
    borderColor: '#10B981',
  },
  cornerBL: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    width: 40,
    height: 40,
    borderBottomWidth: 3,
    borderLeftWidth: 3,
    borderColor: '#10B981',
  },
  cornerBR: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 40,
    height: 40,
    borderBottomWidth: 3,
    borderRightWidth: 3,
    borderColor: '#10B981',
  },
  arrowContainer: {
    position: 'absolute',
    top: 50,
    alignSelf: 'center',
  },
  arrowEmoji: {
    fontSize: 48,
  },
  controls: {
    padding: 24,
    backgroundColor: 'white',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
  },
  instruction: {
    textAlign: 'center',
    color: '#111827',
    fontWeight: '600',
  },
  subInstruction: {
    textAlign: 'center',
    color: '#6B7280',
    marginTop: 8,
    marginBottom: 24,
  },
  captureButton: {
    borderRadius: 12,
    elevation: 2,
  },
  captureButtonContent: {
    paddingVertical: 8,
  },
  reviewContainer: {
    padding: 16,
  },
  reviewHeader: {
    padding: 20,
    borderRadius: 12,
    backgroundColor: 'white',
    marginBottom: 20,
  },
  reviewTitle: {
    textAlign: 'center',
    color: '#111827',
    fontWeight: '600',
  },
  reviewSubtitle: {
    textAlign: 'center',
    color: '#6B7280',
    marginTop: 8,
  },
  imagesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  imageCard: {
    width: '48%',
    marginBottom: 16,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: 'white',
  },
  angleLabel: {
    padding: 12,
    textAlign: 'center',
    backgroundColor: '#F9FAFB',
    color: '#374151',
  },
  previewImage: {
    width: '100%',
    height: 180,
  },
  retakeButton: {
    position: 'absolute',
    bottom: 8,
    right: 8,
    backgroundColor: 'rgba(255,255,255,0.9)',
  },
  reviewActions: {
    flexDirection: 'row',
    marginTop: 20,
    gap: 12,
  },
  retakeAllButton: {
    flex: 1,
  },
  completeButton: {
    flex: 2,
  },
  completeButtonContent: {
    paddingVertical: 8,
  },
  processingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  processingCard: {
    padding: 32,
    borderRadius: 16,
    alignItems: 'center',
  },
  processingText: {
    marginTop: 16,
    color: '#374151',
  },
});