import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { RootState } from '../store/store';

const API_URL = 'http://kmou.n2nai.io:5200/api/v1';

// Custom base query with logging
const baseQueryWithLogging = fetchBaseQuery({
  baseUrl: API_URL,
  prepareHeaders: async (headers, { getState }) => {
    const token = (getState() as RootState).auth.token;
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }
    return headers;
  },
});

const baseQueryWithLogger = async (args: any, api: any, extraOptions: any) => {
  // Build full URL for logging
  const fullUrl = `${API_URL}${args.url}`;
  
  // Log request
  console.log('🚀 API Request:', {
    fullUrl,
    url: args.url,
    method: args.method || 'GET',
    body: args.body instanceof FormData ? 'FormData' : args.body,
  });

  try {
    const startTime = Date.now();
    const result = await baseQueryWithLogging(args, api, extraOptions);
    const duration = Date.now() - startTime;

    // Log response
    if (result.error) {
      console.error('❌ API Error:', {
        url: fullUrl,
        error: result.error,
        status: result.error.status,
        data: result.error.data,
        duration: `${duration}ms`,
      });
    } else {
      console.log('✅ API Response:', {
        url: fullUrl,
        data: result.data,
        duration: `${duration}ms`,
      });
    }

    return result;
  } catch (error) {
    console.error('🔥 Network Error:', {
      url: fullUrl,
      error: error,
      message: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined,
    });
    throw error;
  }
};

export const baseApi = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithLogger,
  tagTypes: ['Farmer', 'Farm', 'Attendance', 'Performance', 'FaceEnrollment', 'Statistics'],
  endpoints: () => ({}),
});