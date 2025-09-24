# AI Face Coffee Farm - Mobile App

React Native mobile application for the AI Face Coffee Farm attendance system.

## Features

- 👤 Face recognition check-in/out
- 👥 Farmer management
- 📸 Face enrollment with multi-angle capture
- 📊 Dashboard with real-time statistics
- 🔐 Secure authentication
- 📱 Native camera integration

## Tech Stack

- React Native with Expo
- TypeScript
- Redux Toolkit + RTK Query
- React Navigation
- React Native Paper (Material Design)
- Expo Camera

## Prerequisites

- Node.js 16+
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- Expo Go app on your phone for testing

## Installation

```bash
# Install dependencies
npm install

# Start the development server
npm start
```

## Running the App

### On Physical Device

1. Install Expo Go app on your phone
2. Scan the QR code from the terminal
3. The app will load in Expo Go

### On iOS Simulator

```bash
npm run ios
```

### On Android Emulator

```bash
npm run android
```

## Project Structure

```
mobile/
├── App.tsx                 # Main app entry point
├── src/
│   ├── navigation/        # Navigation configuration
│   ├── screens/          # Screen components
│   ├── components/       # Reusable components
│   ├── services/         # API services (RTK Query)
│   ├── store/           # Redux store configuration
│   └── theme/           # Theme configuration
├── assets/              # Images and static assets
└── package.json
```

## API Configuration

The app connects to the backend API. Update the API URL in `src/services/api.ts`:

```typescript
const API_URL = 'http://sarm.n2nai.io:5100/api/v1';
```

## Mock Mode

The app works in mock mode when the backend is running without Firebase. Face recognition will return simulated results.

## Login Credentials (Mock Mode)

- Username: `admin`
- Password: `admin123`

## Building for Production

### iOS

```bash
expo build:ios
```

### Android

```bash
expo build:android
```

## Troubleshooting

### Camera Permission Issues

Make sure camera permissions are granted in device settings.

### Network Issues

Ensure your device is on the same network as the backend server or the backend is accessible publicly.