import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAppSelector } from '../store/hooks';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// Screens
import LoginScreen from '../screens/LoginScreen';
import HomeScreen from '../screens/HomeScreen';
import FarmersScreen from '../screens/FarmersScreen';
import CheckInScreen from '../screens/CheckInScreen';
import ProfileScreen from '../screens/ProfileScreen';
import FarmerDetailScreen from '../screens/FarmerDetailScreen';
import FaceEnrollmentScreen from '../screens/FaceEnrollmentScreen';
import FaceEnrollmentWelcomeScreen from '../screens/FaceEnrollmentWelcomeScreen';
import SelectFarmerScreen from '../screens/SelectFarmerScreen';
import AddFarmerScreen from '../screens/AddFarmerScreen';
import CoffeeBeansScreen from '../screens/CoffeeBeansScreen';
import CoffeeLeavesScreen from '../screens/CoffeeLeavesScreen';
import CoffeeBeansResultScreen from '../screens/CoffeeBeansResultScreen';
import CoffeeLeavesResultScreen from '../screens/CoffeeLeavesResultScreen';
import MapAttendanceScreen from '../screens/MapAttendanceScreen';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Farmers') {
            iconName = focused ? 'account-group' : 'account-group-outline';
          } else if (route.name === 'CheckIn') {
            iconName = focused ? 'face-recognition' : 'face-recognition';
          } else if (route.name === 'CoffeeBeans') {
            iconName = focused ? 'coffee' : 'coffee-outline';
          } else if (route.name === 'CoffeeLeaves') {
            iconName = focused ? 'leaf' : 'leaf';
          } else if (route.name === 'MapAttendance') {
            iconName = focused ? 'map-marker-multiple' : 'map-marker-multiple-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'account' : 'account-outline';
          }

          return <Icon name={iconName!} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#10B981',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} options={{ title: 'Dashboard' }} />
      <Tab.Screen name="Farmers" component={FarmersScreen} />
      <Tab.Screen name="CheckIn" component={CheckInScreen} options={{ title: 'Check In/Out' }} />
      <Tab.Screen name="CoffeeBeans" component={CoffeeBeansScreen} options={{ title: 'Coffee Beans' }} />
      <Tab.Screen name="CoffeeLeaves" component={CoffeeLeavesScreen} options={{ title: 'Coffee Leaves' }} />
      <Tab.Screen name="MapAttendance" component={MapAttendanceScreen} options={{ title: 'Map' }} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

function MainStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen 
        name="MainTabs" 
        component={TabNavigator} 
        options={{ headerShown: false }} 
      />
      <Stack.Screen 
        name="FarmerDetail" 
        component={FarmerDetailScreen} 
        options={{ title: 'Farmer Details' }}
      />
      <Stack.Screen 
        name="FaceEnrollment" 
        component={FaceEnrollmentScreen} 
        options={{ title: 'Face Enrollment' }}
      />
      <Stack.Screen 
        name="FaceEnrollmentWelcome" 
        component={FaceEnrollmentWelcomeScreen} 
        options={{ title: 'Face Enrollment' }}
      />
      <Stack.Screen 
        name="SelectFarmer" 
        component={SelectFarmerScreen} 
        options={{ title: 'Select Farmer' }}
      />
      <Stack.Screen 
        name="AddFarmer" 
        component={AddFarmerScreen} 
        options={{ title: 'Add New Farmer' }}
      />
      <Stack.Screen 
        name="CoffeeBeansResult" 
        component={CoffeeBeansResultScreen} 
        options={{ title: 'Coffee Beans Analysis Result' }}
      />
      <Stack.Screen 
        name="CoffeeLeavesResult" 
        component={CoffeeLeavesResultScreen} 
        options={{ title: 'Coffee Leaves Analysis Result' }}
      />
    </Stack.Navigator>
  );
}

export default function AppNavigator() {
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {!isAuthenticated ? (
        <Stack.Screen name="Login" component={LoginScreen} />
      ) : (
        <Stack.Screen name="Main" component={MainStack} />
      )}
    </Stack.Navigator>
  );
}