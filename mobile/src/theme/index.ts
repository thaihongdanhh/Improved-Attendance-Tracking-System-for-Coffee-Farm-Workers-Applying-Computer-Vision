import { MD3LightTheme as DefaultTheme } from 'react-native-paper';

export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#10B981', // Green
    secondary: '#059669',
    tertiary: '#F59E0B',
    error: '#EF4444',
    background: '#F3F4F6',
    surface: '#FFFFFF',
    surfaceVariant: '#F9FAFB',
    onSurface: '#111827',
    onSurfaceVariant: '#6B7280',
  },
};