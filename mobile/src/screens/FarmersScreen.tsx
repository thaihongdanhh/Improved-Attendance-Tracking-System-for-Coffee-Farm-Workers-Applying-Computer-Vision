import React, { useState } from 'react';
import {
  View,
  FlatList,
  StyleSheet,
  RefreshControl,
} from 'react-native';
import {
  List,
  Searchbar,
  FAB,
  Surface,
  Text,
  ActivityIndicator,
  Chip,
  Dialog,
  Portal,
  TextInput,
  Button,
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useGetFarmersQuery, useCreateFarmerMutation } from '../services';

export default function FarmersScreen() {
  const navigation = useNavigation<any>();
  const { data: farmers = [], isLoading, refetch } = useGetFarmersQuery({});
  const [createFarmer] = useCreateFarmerMutation();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [dialogVisible, setDialogVisible] = useState(false);
  const [formData, setFormData] = useState({
    farmer_code: '',
    full_name: '',
    phone: '',
    farm_id: 'default_farm',
  });

  const onRefresh = React.useCallback(async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  }, []);

  const filteredFarmers = farmers.filter((farmer: any) => {
    const searchLower = searchQuery.toLowerCase();
    const fullName = farmer.full_name || farmer.name || '';
    const farmerCode = farmer.farmer_code || '';
    return (
      fullName.toLowerCase().includes(searchLower) ||
      farmerCode.toLowerCase().includes(searchLower)
    );
  });

  const handleCreateFarmer = async () => {
    try {
      await createFarmer(formData).unwrap();
      setDialogVisible(false);
      setFormData({
        farmer_code: '',
        full_name: '',
        phone: '',
        farm_id: 'default_farm',
      });
      refetch();
    } catch (error) {
      console.error('Failed to create farmer:', error);
    }
  };

  const renderFarmer = ({ item }: { item: any }) => (
    <Surface style={styles.farmerCard} elevation={1}>
      <List.Item
        title={item.full_name || item.name || 'Unknown'}
        description={`Code: ${item.farmer_code || 'N/A'}\nPhone: ${item.phone || 'N/A'}`}
        left={(props) => <List.Icon {...props} icon="account" />}
        right={() => (
          <View style={styles.chipContainer}>
            <Chip
              mode="flat"
              style={[
                styles.chip,
                { backgroundColor: (item.has_face_enrolled || item.face_enrolled) ? '#D1FAE5' : '#FEF3C7' }
              ]}
              textStyle={{ fontSize: 12 }}
            >
              {(item.has_face_enrolled || item.face_enrolled) ? 'Enrolled' : 'Not Enrolled'}
            </Chip>
          </View>
        )}
        onPress={() => navigation.navigate('FarmerDetail', { farmerId: item.id })}
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
      <Searchbar
        placeholder="Search farmers..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchbar}
      />

      <FlatList
        data={filteredFarmers}
        keyExtractor={(item) => item.id}
        renderItem={renderFarmer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge" style={styles.emptyText}>
              No farmers found
            </Text>
          </View>
        }
      />

      <Portal>
        <Dialog visible={dialogVisible} onDismiss={() => setDialogVisible(false)}>
          <Dialog.Title>Add New Farmer</Dialog.Title>
          <Dialog.Content>
            <TextInput
              label="Farmer Code"
              value={formData.farmer_code}
              onChangeText={(text) => setFormData({ ...formData, farmer_code: text })}
              style={styles.input}
              mode="outlined"
            />
            <TextInput
              label="Full Name"
              value={formData.full_name}
              onChangeText={(text) => setFormData({ ...formData, full_name: text })}
              style={styles.input}
              mode="outlined"
            />
            <TextInput
              label="Phone Number"
              value={formData.phone}
              onChangeText={(text) => setFormData({ ...formData, phone: text })}
              style={styles.input}
              mode="outlined"
              keyboardType="phone-pad"
            />
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setDialogVisible(false)}>Cancel</Button>
            <Button onPress={handleCreateFarmer}>Save</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => setDialogVisible(true)}
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
  searchbar: {
    margin: 16,
    elevation: 2,
  },
  listContent: {
    paddingBottom: 80,
  },
  farmerCard: {
    marginHorizontal: 16,
    marginVertical: 8,
    borderRadius: 8,
    backgroundColor: 'white',
    minHeight: 80,
    paddingVertical: 4,
  },
  chipContainer: {
    justifyContent: 'center',
    paddingRight: 8,
  },
  chip: {
    height: 35,
    paddingHorizontal: 12,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  emptyText: {
    color: '#6B7280',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#10B981',
  },
  input: {
    marginBottom: 12,
  },
});