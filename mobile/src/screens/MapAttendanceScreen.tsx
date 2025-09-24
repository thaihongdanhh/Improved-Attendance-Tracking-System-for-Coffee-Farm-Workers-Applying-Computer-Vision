import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
  Linking,
  Dimensions,
} from 'react-native';
import {
  Surface,
  Text,
  Button,
  Card,
  Chip,
  ActivityIndicator,
  Searchbar,
  FAB,
  List,
  Divider,
  Badge,
  Modal,
  Portal,
} from 'react-native-paper';
import * as Location from 'expo-location';
import { format } from 'date-fns';
import MapView, { Marker } from 'react-native-maps';
import { useGetFarmsQuery } from '../services/farms.api';
import { useGetTodayAttendancesQuery } from '../services/attendance.api';

interface FarmWithStats {
  id: string;
  farm_code?: string;
  farm_name?: string;
  name?: string; // Some farms use 'name' instead of 'farm_name'
  location?: {
    lat: number;
    lng: number;
  };
  coordinates?: {
    latitude: number;
    longitude: number;
  };
  address?: string;
  area_hectares?: number;
  manager_name?: string;
  owner?: string; // Some farms use 'owner' instead of 'manager_name'
  contact_phone?: string;
  contact?: string; // Some farms use 'contact' instead of 'contact_phone'
  is_active?: boolean;
  today_attendances?: number;
  active_farmers?: number;
  total_farmers?: number;
}

const { width, height } = Dimensions.get('window');

export default function MapAttendanceScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const [currentLocation, setCurrentLocation] = useState<{latitude: number, longitude: number} | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedFarm, setSelectedFarm] = useState<FarmWithStats | null>(null);
  const [showFarmModal, setShowFarmModal] = useState(false);
  const [mapRegion, setMapRegion] = useState({
    latitude: 11.5,  // Center of Vietnam coffee regions
    longitude: 108.0,
    latitudeDelta: 3.0, // Zoom out to show all Vietnam
    longitudeDelta: 3.0,
  });

  // Get all farms data
  const { 
    data: farms, 
    isLoading: farmsLoading, 
    error: farmsError,
    refetch: refetchFarms
  } = useGetFarmsQuery({});

  // Get today's attendance data for all farms
  const { 
    data: todayData, 
    refetch: refetchAttendance 
  } = useGetTodayAttendancesQuery({});

  const farmsList: FarmWithStats[] = farms || [];
  const todayAttendances = todayData?.attendances || [];

  // Debug logging
  console.log('🏡 Farms data:', {
    farmsCount: farmsList.length,
    farmsWithCoords: farmsList.filter(f => 
      (f.location && f.location.lat && f.location.lng) || 
      (f.coordinates && f.coordinates.latitude && f.coordinates.longitude)
    ).length,
    sampleFarm: farmsList[0],
  });

  // Filter farms based on search query
  const filteredFarms = farmsList.filter(farm => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    const farmName = farm.farm_name || farm.name || '';
    const farmCode = farm.farm_code || '';
    const managerName = farm.manager_name || farm.owner || '';
    return (
      farmName.toLowerCase().includes(query) ||
      farmCode.toLowerCase().includes(query) ||
      managerName.toLowerCase().includes(query)
    );
  });

  // Enhance farms with attendance statistics
  const farmsWithStats: FarmWithStats[] = filteredFarms.map(farm => {
    const farmAttendances = todayAttendances.filter(att => att.farm_id === farm.id);
    return {
      ...farm,
      today_attendances: farmAttendances.length,
      active_farmers: farmAttendances.filter(att => att.status === 'working').length,
      total_farmers: farmAttendances.length,
    };
  });

  // Get user's current location
  useEffect(() => {
    getCurrentLocation();
  }, []);

  const getCurrentLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(
          'Permission Denied',
          'Location permission is required to show distances to attendance locations.'
        );
        return;
      }

      const location = await Location.getCurrentPositionAsync({});
      setCurrentLocation({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
      });
    } catch (error) {
      console.error('Error getting location:', error);
    }
  };

  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
    const R = 6371; // Radius of the Earth in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const d = R * c; // Distance in kilometers
    return d;
  };

  const getDistanceText = (latitude: number, longitude: number): string => {
    if (!currentLocation) return '';
    const distance = calculateDistance(
      currentLocation.latitude,
      currentLocation.longitude,
      latitude,
      longitude
    );
    if (distance < 1) {
      return `${Math.round(distance * 1000)}m away`;
    }
    return `${distance.toFixed(1)}km away`;
  };

  const openInMaps = (latitude: number, longitude: number, name: string) => {
    const url = `https://www.google.com/maps/search/?api=1&query=${latitude},${longitude}`;
    Linking.openURL(url);
  };

  const handleFarmPress = (farm: FarmWithStats) => {
    setSelectedFarm(farm);
    setShowFarmModal(true);
  };

  const getMarkerColor = (farm: FarmWithStats) => {
    if (farm.is_active === false) return '#6B7280'; // Gray for inactive
    if (farm.active_farmers === 0) return '#EF4444'; // Red for no active farmers
    if (farm.active_farmers && farm.active_farmers > 0) return '#10B981'; // Green for active farmers
    return '#3B82F6'; // Blue for default (no activity data yet)
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'working': return '#3B82F6';
      case 'completed': return '#10B981';
      default: return '#6B7280';
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      await Promise.all([refetchFarms(), refetchAttendance()]);
      await getCurrentLocation();
    } finally {
      setRefreshing(false);
    }
  };

  if (farmsLoading && !refreshing) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" />
        <Text style={styles.loadingText}>Loading farms data...</Text>
      </View>
    );
  }

  if (farmsError) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>Error loading farms data</Text>
        <Button mode="contained" onPress={() => refetchFarms()}>
          Retry
        </Button>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header with Search Controls */}
      <Surface style={styles.controlsContainer} elevation={2}>
        <Searchbar
          placeholder="Search farms..."
          onChangeText={setSearchQuery}
          value={searchQuery}
          style={styles.searchBar}
        />
        
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          style={styles.chipContainer}
          contentContainerStyle={styles.chipContent}
        >
          <Chip
            mode="outlined"
            style={styles.chip}
            icon="barn"
          >
            Total Farms ({farmsWithStats.length})
          </Chip>
          
          <Chip
            style={styles.chip}
            icon="account-check"
            selectedColor="#10B981"
          >
            Active ({farmsWithStats.filter(f => f.active_farmers && f.active_farmers > 0).length})
          </Chip>
          
          <Chip
            style={styles.chip}
            icon="account-clock"
            selectedColor="#3B82F6"
          >
            Today ({farmsWithStats.reduce((sum, f) => sum + (f.today_attendances || 0), 0)})
          </Chip>
        </ScrollView>
      </Surface>

      {/* Map */}
      <MapView
        style={styles.map}
        region={mapRegion}
        onRegionChangeComplete={setMapRegion}
        showsUserLocation={true}
        showsMyLocationButton={true}
      >
        {farmsWithStats
          .filter(farm => {
            // Check if farm has coordinates in either format
            const hasLocation = (farm.location && farm.location.lat && farm.location.lng);
            const hasCoordinates = (farm.coordinates && farm.coordinates.latitude && farm.coordinates.longitude);
            const hasValidCoords = hasLocation || hasCoordinates;
            
            if (hasValidCoords) {
              console.log('✅ Farm with coords:', {
                id: farm.id,
                name: farm.farm_name || farm.name,
                location: farm.location,
                coordinates: farm.coordinates
              });
            } else {
              console.log('❌ Farm without coords:', {
                id: farm.id,
                name: farm.farm_name || farm.name,
                location: farm.location,
                coordinates: farm.coordinates
              });
            }
            
            return hasValidCoords;
          })
          .map((farm, index) => {
            // Get coordinates from either location or coordinates field
            let coords;
            if (farm.location && farm.location.lat && farm.location.lng) {
              coords = { latitude: farm.location.lat, longitude: farm.location.lng };
            } else if (farm.coordinates && farm.coordinates.latitude && farm.coordinates.longitude) {
              coords = { latitude: farm.coordinates.latitude, longitude: farm.coordinates.longitude };
            } else {
              // Fallback - shouldn't happen due to filter, but just in case
              coords = { latitude: 0, longitude: 0 };
            }
              
            console.log('🗺️ Creating marker:', {
              index,
              id: farm.id,
              name: farm.farm_name || farm.name,
              coords,
              farmLocation: farm.location,
              farmCoordinates: farm.coordinates,
              pinColor: getMarkerColor(farm)
            });
              
            return (
              <Marker
                key={farm.id}
                coordinate={coords}
                title={farm.farm_name || farm.name || 'Unknown Farm'}
                description={`${farm.active_farmers || 0} active farmers today`}
                pinColor={getMarkerColor(farm)}
                onPress={() => handleFarmPress(farm)}
              />
            );
          })
        }
        
        
        {/* User location marker if available */}
        {currentLocation && (
          <Marker
            coordinate={{
              latitude: currentLocation.latitude,
              longitude: currentLocation.longitude,
            }}
            title="Your Location"
            pinColor="#2196F3"
          />
        )}
      </MapView>

      {/* Farm Detail Modal */}
      <Portal>
        <Modal
          visible={showFarmModal}
          onDismiss={() => setShowFarmModal(false)}
          contentContainerStyle={styles.modalContainer}
        >
          {selectedFarm && (
            <Card style={styles.farmDetailCard}>
              <Card.Content>
                <View style={styles.farmHeader}>
                  <View>
                    <Text style={styles.farmName}>{selectedFarm.farm_name || selectedFarm.name || 'Unknown Farm'}</Text>
                    <Text style={styles.farmCode}>Code: {selectedFarm.farm_code || 'N/A'}</Text>
                  </View>
                  <Badge 
                    style={[
                      styles.farmStatusBadge, 
                      { backgroundColor: selectedFarm.is_active !== false ? '#10B981' : '#6B7280' }
                    ]}
                  >
                    {selectedFarm.is_active !== false ? 'Active' : 'Inactive'}
                  </Badge>
                </View>

                <Divider style={styles.divider} />

                {/* Farm Statistics */}
                <View style={styles.farmStatsContainer}>
                  <Text style={styles.sectionTitle}>Today's Activity</Text>
                  <View style={styles.farmStatsRow}>
                    <View style={styles.farmStatItem}>
                      <Text style={[styles.statNumber, {color: '#3B82F6'}]}>
                        {selectedFarm.today_attendances || 0}
                      </Text>
                      <Text style={styles.statLabel}>Total Check-ins</Text>
                    </View>
                    <View style={styles.farmStatItem}>
                      <Text style={[styles.statNumber, {color: '#10B981'}]}>
                        {selectedFarm.active_farmers || 0}
                      </Text>
                      <Text style={styles.statLabel}>Currently Working</Text>
                    </View>
                  </View>
                </View>

                {/* Farm Information */}
                <View style={styles.farmInfoContainer}>
                  <Text style={styles.sectionTitle}>Farm Details</Text>
                  
                  {(selectedFarm.manager_name || selectedFarm.owner) && (
                    <List.Item
                      title="Manager/Owner"
                      description={selectedFarm.manager_name || selectedFarm.owner}
                      left={(props) => <List.Icon {...props} icon="account-tie" />}
                    />
                  )}
                  
                  {selectedFarm.area_hectares && (
                    <List.Item
                      title="Area"
                      description={`${selectedFarm.area_hectares} hectares`}
                      left={(props) => <List.Icon {...props} icon="texture-box" />}
                    />
                  )}
                  
                  {(selectedFarm.address || selectedFarm.location) && (
                    <List.Item
                      title="Address"
                      description={selectedFarm.address || selectedFarm.location || 'N/A'}
                      left={(props) => <List.Icon {...props} icon="map-marker" />}
                    />
                  )}
                  
                  {(selectedFarm.contact_phone || selectedFarm.contact) && (
                    <List.Item
                      title="Contact"
                      description={selectedFarm.contact_phone || selectedFarm.contact}
                      left={(props) => <List.Icon {...props} icon="phone" />}
                    />
                  )}
                  
                  {(selectedFarm.location || selectedFarm.coordinates) && currentLocation && (
                    <List.Item
                      title="Distance"
                      description={getDistanceText(
                        selectedFarm.location?.lat || selectedFarm.coordinates?.latitude || 0,
                        selectedFarm.location?.lng || selectedFarm.coordinates?.longitude || 0
                      )}
                      left={(props) => <List.Icon {...props} icon="map-marker-distance" />}
                    />
                  )}
                </View>

                {/* Action Buttons */}
                <View style={styles.farmActionsContainer}>
                  {(selectedFarm.location || selectedFarm.coordinates) && (
                    <Button
                      mode="outlined"
                      icon="map"
                      onPress={() => {
                        const lat = selectedFarm.location?.lat || selectedFarm.coordinates?.latitude || 0;
                        const lng = selectedFarm.location?.lng || selectedFarm.coordinates?.longitude || 0;
                        const name = selectedFarm.farm_name || selectedFarm.name || 'Farm';
                        openInMaps(lat, lng, name);
                        setShowFarmModal(false);
                      }}
                      style={styles.farmActionButton}
                    >
                      Open in Maps
                    </Button>
                  )}
                  
                  <Button
                    mode="contained"
                    icon="close"
                    onPress={() => setShowFarmModal(false)}
                    style={styles.farmActionButton}
                  >
                    Close
                  </Button>
                </View>
              </Card.Content>
            </Card>
          )}
        </Modal>
      </Portal>

      {/* Floating Action Button */}
      <FAB
        icon="crosshairs-gps"
        style={styles.fab}
        onPress={getCurrentLocation}
        label={currentLocation ? "Update Location" : "Get Location"}
      />
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
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6B7280',
  },
  errorText: {
    fontSize: 16,
    color: '#DC2626',
    marginBottom: 16,
    textAlign: 'center',
  },
  controlsContainer: {
    padding: 16,
    backgroundColor: 'white',
    zIndex: 1,
  },
  searchBar: {
    marginBottom: 12,
  },
  chipContainer: {
    flexDirection: 'row',
  },
  chipContent: {
    paddingRight: 16,
  },
  chip: {
    marginRight: 8,
  },
  map: {
    flex: 1,
    width: width,
    height: height - 160, // Account for header and controls
  },
  modalContainer: {
    backgroundColor: 'white',
    padding: 20,
    margin: 20,
    borderRadius: 12,
    maxHeight: height * 0.8,
  },
  farmDetailCard: {
    backgroundColor: 'white',
  },
  farmHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  farmName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4,
  },
  farmCode: {
    fontSize: 14,
    color: '#6B7280',
  },
  farmStatusBadge: {
    borderRadius: 16,
  },
  farmStatsContainer: {
    marginBottom: 16,
  },
  farmStatsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 12,
  },
  farmStatItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
    textAlign: 'center',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 8,
  },
  farmInfoContainer: {
    marginBottom: 16,
  },
  farmActionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
  },
  farmActionButton: {
    flex: 1,
  },
  divider: {
    marginBottom: 16,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#3B82F6',
  },
});