import React from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  RefreshControl,
} from 'react-native';
import {
  Surface,
  Text,
  Card,
  ActivityIndicator,
  Banner,
  Button,
} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useGetDashboardStatisticsQuery, useGetTodayAttendancesQuery } from '../services';
import { useNavigation } from '@react-navigation/native';

export default function HomeScreen() {
  const navigation = useNavigation();
  const { data: stats, isLoading: statsLoading, refetch: refetchStats } = useGetDashboardStatisticsQuery();
  const { data: todayData, refetch: refetchAttendance } = useGetTodayAttendancesQuery({});
  const [refreshing, setRefreshing] = React.useState(false);
  
  // Extract attendances from the response
  const todayAttendances = todayData?.attendances || [];

  const onRefresh = React.useCallback(async () => {
    setRefreshing(true);
    await Promise.all([refetchStats(), refetchAttendance()]);
    setRefreshing(false);
  }, [refetchStats, refetchAttendance]);

  const StatCard = ({ title, value, icon, color }: any) => (
    <Card style={styles.statCard}>
      <Card.Content style={styles.statContent}>
        <View style={[styles.iconContainer, { backgroundColor: color + '20' }]}>
          <Icon name={icon} size={24} color={color} />
        </View>
        <Text variant="bodyMedium" style={styles.statTitle}>{title}</Text>
        <Text variant="headlineMedium" style={styles.statValue}>
          {value}
        </Text>
      </Card.Content>
    </Card>
  );

  if (statsLoading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {stats?.system.mode === 'mock' && (
        <Banner
          visible={true}
          icon="information"
          style={styles.banner}
        >
          System is running in Mock Mode. Face recognition will return simulated results.
        </Banner>
      )}

      <Text variant="headlineSmall" style={styles.welcome}>
        Welcome to AI Face Coffee Farm
      </Text>
      <Text variant="bodyMedium" style={styles.subtitle}>
        Face Recognition Attendance System
      </Text>

      <View style={styles.statsGrid}>
        <StatCard
          title="Total Farmers"
          value={stats?.farmers.total || 0}
          icon="account-group"
          color="#10B981"
        />
        <StatCard
          title="Active Today"
          value={stats?.attendances.today || 0}
          icon="account-clock"
          color="#3B82F6"
        />
        <StatCard
          title="Working Now"
          value={stats?.attendances.active || 0}
          icon="account-check"
          color="#F59E0B"
        />
        <StatCard
          title="Face Enrolled"
          value={`${stats?.farmers.with_face_enrolled || 0}/${stats?.farmers.total || 0}`}
          icon="face-recognition"
          color="#8B5CF6"
        />
      </View>

      <Surface style={styles.recentSection} elevation={1}>
        <Text variant="titleMedium" style={styles.sectionTitle}>
          Recent Activities
        </Text>
        {todayAttendances.length === 0 ? (
          <Text variant="bodyMedium" style={styles.noData}>
            No attendance records for today
          </Text>
        ) : (
          <View>
            {todayAttendances.slice(0, 5).map((attendance: any) => (
              <View key={attendance.id} style={styles.activityItem}>
                <Icon 
                  name={attendance.status === 'working' ? 'login' : 'logout'} 
                  size={20} 
                  color={attendance.status === 'working' ? '#10B981' : '#6B7280'} 
                />
                <Text variant="bodyMedium" style={styles.activityText}>
                  {attendance.farmer_name || 'Unknown'} - {attendance.status === 'working' ? 'Checked In' : 'Completed'}
                </Text>
                <Text variant="bodySmall" style={styles.activityTime}>
                  {new Date(attendance.check_in_time).toLocaleTimeString()}
                </Text>
              </View>
            ))}
          </View>
        )}
      </Surface>

      {/* Navigation Button to Map Attendance */}
      <Surface style={styles.mapButtonSection} elevation={1}>
        <Button
          mode="contained"
          icon="map-marker-multiple"
          onPress={() => navigation.navigate('MainTabs', { screen: 'MapAttendance' })}
          style={styles.mapButton}
          contentStyle={styles.mapButtonContent}
        >
          View Attendance Map
        </Button>
        <Text variant="bodySmall" style={styles.mapButtonDescription}>
          See attendance locations and track farmer check-ins on the map
        </Text>
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
  banner: {
    backgroundColor: '#FEF3C7',
    marginBottom: 16,
  },
  welcome: {
    paddingHorizontal: 20,
    paddingTop: 20,
    color: '#111827',
  },
  subtitle: {
    paddingHorizontal: 20,
    paddingBottom: 20,
    color: '#6B7280',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 10,
    paddingTop: 10,
  },
  statCard: {
    width: '47%',
    margin: '1.5%',
    backgroundColor: 'white',
  },
  statContent: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  statTitle: {
    color: '#6B7280',
    marginBottom: 4,
  },
  statValue: {
    color: '#111827',
    fontWeight: 'bold',
  },
  recentSection: {
    margin: 20,
    padding: 20,
    borderRadius: 12,
    backgroundColor: 'white',
  },
  sectionTitle: {
    marginBottom: 16,
    color: '#111827',
  },
  noData: {
    textAlign: 'center',
    color: '#6B7280',
    paddingVertical: 20,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  activityText: {
    flex: 1,
    marginLeft: 12,
    color: '#374151',
  },
  activityTime: {
    color: '#9CA3AF',
  },
  mapButtonSection: {
    margin: 20,
    marginTop: 0,
    padding: 20,
    borderRadius: 12,
    backgroundColor: 'white',
    alignItems: 'center',
  },
  mapButton: {
    width: '100%',
    backgroundColor: '#3B82F6',
    marginBottom: 12,
  },
  mapButtonContent: {
    paddingVertical: 8,
  },
  mapButtonDescription: {
    textAlign: 'center',
    color: '#6B7280',
    lineHeight: 20,
  },
});