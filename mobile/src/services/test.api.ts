import { baseApi } from './api';

export interface SystemStatistics {
  farms: {
    total: number;
    active: number;
  };
  farmers: {
    total: number;
    active: number;
  };
  attendances: {
    today: number;
    active: number;
  };
  system: {
    mode: 'mock' | 'production';
    face_service: 'mock' | 'production';
  };
}

export interface CreateSampleDataResponse {
  success: boolean;
  message: string;
  data: {
    farms_created: number;
    farmers_created: number;
    attendances_created: number;
  };
}

export interface SimulateFaceVerifyResponse {
  verified: boolean;
  farmer_id?: string;
  farmer_name?: string;
  confidence?: number;
  message: string;
}

export const testApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    // Create sample data
    createSampleData: builder.mutation<CreateSampleDataResponse, void>({
      query: () => ({
        url: '/test/create-sample-data',
        method: 'POST',
      }),
      invalidatesTags: [
        { type: 'Farmer', id: 'LIST' },
        { type: 'Farm', id: 'LIST' },
        { type: 'Attendance', id: 'LIST' },
      ],
    }),

    // Get system statistics
    getSystemStatistics: builder.query<SystemStatistics, void>({
      query: () => '/test/statistics',
    }),

    // Simulate face verification
    simulateFaceVerify: builder.mutation<SimulateFaceVerifyResponse, { farmer_id?: string }>({
      query: (params) => ({
        url: '/test/simulate-face-verify',
        method: 'POST',
        params,
      }),
    }),

    // Clear all data
    clearAllData: builder.mutation<{ message: string }, void>({
      query: () => ({
        url: '/test/clear-all-data',
        method: 'DELETE',
      }),
      invalidatesTags: [
        { type: 'Farmer', id: 'LIST' },
        { type: 'Farm', id: 'LIST' },
        { type: 'Attendance', id: 'LIST' },
        { type: 'Performance', id: 'LIST' },
      ],
    }),
  }),
});

export const {
  useCreateSampleDataMutation,
  useGetSystemStatisticsQuery,
  useSimulateFaceVerifyMutation,
  useClearAllDataMutation,
} = testApi;