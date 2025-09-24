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
  Button,
  Divider,
  ActivityIndicator,
  List,
} from 'react-native-paper';
import { useRoute, useNavigation } from '@react-navigation/native';
import { format } from 'date-fns';
import { useGetFarmerQuery, useGetFarmerAttendancesQuery } from '../services';

export default function FarmerDetailScreen() {
  const route = useRoute<any>();
  const navigation = useNavigation<any>();
  const { farmerId } = route.params;

  const { data: farmer, isLoading: farmerLoading } = useGetFarmerQuery(farmerId);
  const { data: attendanceData, isLoading: attendancesLoading } = useGetFarmerAttendancesQuery(farmerId);
  const attendances = attendanceData?.attendances || [];

  if (farmerLoading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  if (!farmer) {
    return (
      <View style={styles.centerContainer}>
        <Text>Farmer not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Surface style={styles.header} elevation={1}>
        <Avatar.Text 
          size={80} 
          label={(farmer.full_name || farmer.name || 'F').charAt(0).toUpperCase()} 
        />
        <Text variant="headlineSmall" style={styles.name}>
          {farmer.full_name || farmer.name || 'Unknown'}
        </Text>
        <Text variant="bodyMedium" style={styles.code}>
          Code: {farmer.farmer_code || 'N/A'}
        </Text>
      </Surface>

      <Surface style={styles.infoSection} elevation={1}>
        <Text variant="titleMedium" style={styles.sectionTitle}>
          Information
        </Text>
        <Divider />
        
        <View style={styles.infoRow}>
          <Text style={styles.label}>Phone:</Text>
          <Text style={styles.value}>{farmer.phone || 'N/A'}</Text>
        </View>
        
        <View style={styles.infoRow}>
          <Text style={styles.label}>Date of Birth:</Text>
          <Text style={styles.value}>
            {farmer.date_of_birth 
              ? format(new Date(farmer.date_of_birth), 'dd/MM/yyyy')
              : 'N/A'}
          </Text>
        </View>
        
        <View style={styles.infoRow}>
          <Text style={styles.label}>Gender:</Text>
          <Text style={styles.value}>{farmer.gender || 'N/A'}</Text>
        </View>
        
        <View style={styles.infoRow}>
          <Text style={styles.label}>Farm:</Text>
          <Text style={styles.value}>{farmer.farm_name || farmer.farm_id}</Text>
        </View>
        
        <View style={styles.infoRow}>
          <Text style={styles.label}>Face Enrolled:</Text>
          <Text style={[
            styles.value,
            { color: (farmer.has_face_enrolled || farmer.face_enrolled) ? '#10B981' : '#F59E0B' }
          ]}>
            {(farmer.has_face_enrolled || farmer.face_enrolled) ? 'Yes' : 'No'}
          </Text>
        </View>
      </Surface>

      <View style={styles.buttonContainer}>
        {!(farmer.has_face_enrolled || farmer.face_enrolled) && (
          <Button
            mode="contained"
            onPress={() => navigation.navigate('FaceEnrollment', { 
              farmerId: farmer.id,
              farmerName: farmer.full_name || farmer.name || 'Unknown'
            })}
            style={styles.enrollButton}
          >
            Enroll Face
          </Button>
        )}
      </View>

      <Surface style={styles.attendanceSection} elevation={1}>
        <Text variant="titleMedium" style={styles.sectionTitle}>
          Recent Attendance
        </Text>
        <Divider />
        
        {attendancesLoading ? (
          <ActivityIndicator style={styles.loading} />
        ) : attendances.length === 0 ? (
          <Text style={styles.noData}>No attendance records</Text>
        ) : (
          attendances.slice(0, 10).map((attendance: any) => (
            <List.Item
              key={attendance.id}
              title={format(new Date(attendance.date), 'dd/MM/yyyy')}
              description={(() => {
                const checkIn = format(new Date(attendance.check_in_time), 'HH:mm');
                const checkOut = attendance.check_out_time 
                  ? format(new Date(attendance.check_out_time), 'HH:mm')
                  : 'Working';
                const duration = attendance.work_duration_minutes
                  ? `${Math.floor(attendance.work_duration_minutes / 60)}h ${attendance.work_duration_minutes % 60}m`
                  : '';
                return `Check In: ${checkIn} - Check Out: ${checkOut}${duration ? ` (${duration})` : ''}`;
              })()}
              left={(props) => <List.Icon {...props} icon="clock-outline" />}
            />
          ))
        )}
      </Surface>
    </ScrollView>
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
  code: {
    color: '#6B7280',
    marginTop: 4,
  },
  infoSection: {
    marginTop: 16,
    padding: 20,
    backgroundColor: 'white',
  },
  sectionTitle: {
    marginBottom: 16,
    color: '#111827',
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  label: {
    color: '#6B7280',
  },
  value: {
    color: '#111827',
    fontWeight: '500',
  },
  buttonContainer: {
    padding: 20,
  },
  enrollButton: {
    paddingVertical: 8,
  },
  attendanceSection: {
    marginTop: 16,
    marginBottom: 30,
    backgroundColor: 'white',
  },
  loading: {
    paddingVertical: 20,
  },
  noData: {
    textAlign: 'center',
    color: '#6B7280',
    paddingVertical: 20,
  },
});