import React, { useState } from 'react';
import {
  View,
  FlatList,
  StyleSheet,
} from 'react-native';
import {
  Searchbar,
  List,
  Surface,
  Text,
  ActivityIndicator,
  Chip,
  IconButton,
  FAB,
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useGetFarmersQuery } from '../services';

export default function SelectFarmerScreen() {
  const navigation = useNavigation<any>();
  const { data: farmers = [], isLoading } = useGetFarmersQuery({});
  const [searchQuery, setSearchQuery] = useState('');

  const filteredFarmers = farmers.filter((farmer: any) => {
    const searchLower = searchQuery.toLowerCase();
    const fullName = farmer.full_name || farmer.name || '';
    const farmerCode = farmer.farmer_code || '';
    return (
      fullName.toLowerCase().includes(searchLower) ||
      farmerCode.toLowerCase().includes(searchLower)
    );
  });

  const notEnrolledFarmers = filteredFarmers.filter((farmer: any) => !farmer.face_enrolled);

  const renderFarmer = ({ item }: { item: any }) => (
    <Surface style={styles.farmerCard} elevation={1}>
      <List.Item
        title={item.full_name}
        description={`Code: ${item.farmer_code} | Phone: ${item.phone || 'N/A'}`}
        left={(props) => (
          <View style={styles.avatarContainer}>
            <List.Icon {...props} icon="account" />
            {!item.face_enrolled && (
              <View style={styles.newBadge}>
                <Text style={styles.newBadgeText}>New</Text>
              </View>
            )}
          </View>
        )}
        right={() => (
          <IconButton
            icon="chevron-right"
            size={24}
            onPress={() => navigation.navigate('FaceEnrollment', {
              farmerId: item.id,
              farmerName: item.full_name,
              isEnrolled: item.face_enrolled
            })}
          />
        )}
        onPress={() => navigation.navigate('FaceEnrollment', {
          farmerId: item.id,
          farmerName: item.full_name,
          isEnrolled: item.face_enrolled
        })}
      />
    </Surface>
  );

  if (isLoading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Surface style={styles.header} elevation={2}>
        <Text variant="titleLarge" style={styles.headerTitle}>
          Select Farmer
        </Text>
        <Text variant="bodyMedium" style={styles.headerSubtitle}>
          Choose a farmer to enroll their face
        </Text>
      </Surface>

      <Searchbar
        placeholder="Search by name or code..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchbar}
      />

      {notEnrolledFarmers.length > 0 && (
        <Surface style={styles.suggestionBanner} elevation={1}>
          <Text variant="labelMedium" style={styles.suggestionTitle}>
            🆕 Farmers without face enrollment ({notEnrolledFarmers.length})
          </Text>
        </Surface>
      )}

      <FlatList
        data={filteredFarmers}
        keyExtractor={(item) => item.id}
        renderItem={renderFarmer}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge" style={styles.emptyText}>
              {searchQuery ? 'No farmers found matching your search' : 'No farmers registered yet'}
            </Text>
          </View>
        }
      />

      <FAB
        icon="account-plus"
        label="New Farmer"
        style={styles.fab}
        onPress={() => navigation.navigate('AddFarmer')}
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
  searchbar: {
    margin: 16,
    elevation: 2,
  },
  suggestionBanner: {
    marginHorizontal: 16,
    marginBottom: 8,
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#FEF3C7',
  },
  suggestionTitle: {
    color: '#92400E',
  },
  listContent: {
    paddingBottom: 80,
  },
  farmerCard: {
    marginHorizontal: 16,
    marginVertical: 8,
    borderRadius: 8,
    backgroundColor: 'white',
  },
  avatarContainer: {
    position: 'relative',
  },
  newBadge: {
    position: 'absolute',
    top: -4,
    right: -4,
    backgroundColor: '#10B981',
    borderRadius: 10,
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  newBadgeText: {
    color: 'white',
    fontSize: 10,
    fontWeight: 'bold',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  emptyText: {
    color: '#6B7280',
    textAlign: 'center',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#10B981',
  },
});