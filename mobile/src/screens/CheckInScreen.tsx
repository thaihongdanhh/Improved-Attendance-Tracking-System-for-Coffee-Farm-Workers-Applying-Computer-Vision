import React, { useState, useRef } from 'react';
import {
  View,
  StyleSheet,
  Alert,
  Dimensions,
} from 'react-native';
import {
  Surface,
  Text,
  Button,
  SegmentedButtons,
  ActivityIndicator,
  Banner,
} from 'react-native-paper';
import { CameraView, CameraType, useCameraPermissions } from 'expo-camera';
import * as FileSystem from 'expo-file-system';
import { useVerifyFaceMutation, useCheckInMutation, useCheckOutMutation, useGetActiveAttendancesQuery } from '../services';

const { width } = Dimensions.get('window');

export default function CheckInScreen() {
  const cameraRef = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [mode, setMode] = useState<'checkin' | 'checkout'>('checkin');
  const [isProcessing, setIsProcessing] = useState(false);
  
  const [verifyFace] = useVerifyFaceMutation();
  const [checkIn] = useCheckInMutation();
  const [checkOut] = useCheckOutMutation();
  const { data: activeAttendances = [] } = useGetActiveAttendancesQuery({});

  const takePicture = async () => {
    if (!cameraRef.current || isProcessing) return;

    setIsProcessing(true);
    try {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.8,
        base64: true,
      });

      if (!photo || !photo.base64) {
        Alert.alert('Error', 'Failed to capture photo');
        return;
      }

      // Verify face using JSON endpoint
      const verifyResult = await verifyFace({
        image: `data:image/jpeg;base64,${photo.base64}`
      }).unwrap();

      if (!verifyResult.verified) {
        Alert.alert('Error', verifyResult.message || 'Face not recognized');
        return;
      }

      const farmerId = verifyResult.farmer_id!;
      const farmId = verifyResult.farm_id || 'default_farm';
      console.log('Verified farmer:', verifyResult);

      if (mode === 'checkin') {
        // Check in
        await checkIn({
          farmer_id: farmerId,
          farm_id: farmId,
          face_image: `data:image/jpeg;base64,${photo.base64}`,
          location: { latitude: 10.7769, longitude: 106.7009 },
        }).unwrap();

        Alert.alert(
          'Success',
          `Check-in successful!\nWelcome ${verifyResult.farmer_name}!`
        );
      } else {
        // Find active attendance
        const activeAttendance = activeAttendances.find(
          (a) => a.farmer_id === farmerId
        );

        if (!activeAttendance) {
          Alert.alert('Error', 'No active check-in found for this farmer');
          return;
        }

        // Check out
        await checkOut({
          id: activeAttendance.id,
          data: {
            farmer_id: farmerId,
            face_image: `data:image/jpeg;base64,${photo.base64}`,
            location: { latitude: 10.7769, longitude: 106.7009 },
          },
        }).unwrap();

        Alert.alert(
          'Success',
          `Check-out successful!\nHave a great day ${verifyResult.farmer_name}!`
        );
      }
    } catch (error: any) {
      Alert.alert('Error', error.data?.detail || 'An error occurred');
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
        <Text variant="bodyLarge">Camera permission not granted</Text>
        <Button mode="contained" style={styles.button} onPress={requestPermission}>
          Grant Permission
        </Button>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Surface style={styles.header} elevation={2}>
        <SegmentedButtons
          value={mode}
          onValueChange={(value) => setMode(value as 'checkin' | 'checkout')}
          buttons={[
            {
              value: 'checkin',
              label: 'Check In',
              icon: 'login',
            },
            {
              value: 'checkout',
              label: 'Check Out',
              icon: 'logout',
            },
          ]}
          style={styles.segmentedButtons}
        />
      </Surface>

      <View style={styles.cameraContainer}>
        <CameraView
          ref={cameraRef}
          style={styles.camera}
          facing="front"
        />
        <View style={styles.overlay}>
          <View style={styles.faceGuide} />
        </View>
      </View>

      <Surface style={styles.controls} elevation={2}>
        <Text variant="bodyMedium" style={styles.instruction}>
          Position your face within the circle
        </Text>
        
        <Button
          mode="contained"
          onPress={takePicture}
          disabled={isProcessing}
          loading={isProcessing}
          style={styles.captureButton}
          contentStyle={styles.captureButtonContent}
        >
          {isProcessing ? 'Processing...' : `Capture & ${mode === 'checkin' ? 'Check In' : 'Check Out'}`}
        </Button>
      </Surface>

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
  header: {
    padding: 16,
    backgroundColor: 'white',
  },
  segmentedButtons: {
    marginVertical: 8,
  },
  cameraContainer: {
    flex: 1,
    marginVertical: 16,
    marginHorizontal: 16,
    borderRadius: 12,
    overflow: 'hidden',
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
    width: width * 0.6,
    height: width * 0.75,
    borderWidth: 3,
    borderColor: '#10B981',
    borderRadius: width * 0.3,
    backgroundColor: 'transparent',
  },
  controls: {
    padding: 20,
    backgroundColor: 'white',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  instruction: {
    textAlign: 'center',
    marginBottom: 16,
    color: '#6B7280',
  },
  captureButton: {
    borderRadius: 8,
  },
  captureButtonContent: {
    paddingVertical: 8,
  },
  button: {
    marginTop: 16,
  },
});