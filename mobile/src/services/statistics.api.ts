import { baseApi } from './api';

export interface DashboardStatistics {
  farmers: {
    total: number;
    active: number;
    with_face_enrolled: number;
    enrollment_rate: number;
  };
  attendances: {
    today: number;
    active: number;
    checked_out_today: number;
    attendance_rate: number;
  };
  farms: {
    total: number;
    active: number;
  };
  system: {
    mode: 'mock' | 'production';
    face_service: 'mock' | 'production';
    database: 'mock' | 'firebase';
  };
}

export interface SummaryStatistics extends DashboardStatistics {
  summary: {
    total_entities: number;
    system_health: 'healthy' | 'empty';
    last_updated: string;
  };
}

export const statisticsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    // Get dashboard statistics
    getDashboardStatistics: builder.query<DashboardStatistics, void>({
      query: () => '/statistics/dashboard',
      providesTags: ['Statistics'],
    }),

    // Get summary statistics
    getSummaryStatistics: builder.query<SummaryStatistics, void>({
      query: () => '/statistics/summary',
      providesTags: ['Statistics'],
    }),
  }),
});

export const {
  useGetDashboardStatisticsQuery,
  useGetSummaryStatisticsQuery,
} = statisticsApi;