import { baseApi } from './api';

export interface Attendance {
  id: string;
  farmer_id: string;
  farm_id: string;
  date: string;
  check_in_time: string;
  check_out_time?: string;
  check_in_location?: {
    latitude: number;
    longitude: number;
  };
  check_out_location?: {
    latitude: number;
    longitude: number;
  };
  check_in_face_score: number;
  check_out_face_score?: number;
  status: 'working' | 'completed';
  work_hours?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CheckInDto {
  farmer_id: string;
  farm_id: string;
  face_image: string;  // base64 encoded image
  location?: {
    latitude: number;
    longitude: number;
  };
  notes?: string;
}

export interface CheckOutDto {
  farmer_id: string;
  face_image: string;  // base64 encoded image
  location?: {
    latitude: number;
    longitude: number;
  };
  notes?: string;
}

export interface AttendanceStats {
  total_attendances: number;
  active_workers: number;
  completed_shifts: number;
  average_work_hours: number;
}

export const attendanceApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    // Get all attendances
    getAttendances: builder.query<Attendance[], {
      farmer_id?: string;
      farm_id?: string;
      date?: string;
      status?: 'working' | 'completed';
      skip?: number;
      limit?: number;
    }>({
      query: (params) => ({
        url: '/attendance',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Attendance' as const, id })),
              { type: 'Attendance', id: 'LIST' },
            ]
          : [{ type: 'Attendance', id: 'LIST' }],
    }),

    // Get attendance by ID
    getAttendance: builder.query<Attendance, string>({
      query: (id) => `/attendance/${id}`,
      providesTags: (result, error, id) => [{ type: 'Attendance', id }],
    }),

    // Get today's attendances
    getTodayAttendances: builder.query<Attendance[], { farm_id?: string }>({
      query: (params) => ({
        url: '/attendance/today',
        params,
      }),
      providesTags: [{ type: 'Attendance', id: 'TODAY' }],
    }),

    // Get active attendances (currently working)
    getActiveAttendances: builder.query<Attendance[], { farm_id?: string }>({
      query: (params) => ({
        url: '/attendance/active',
        params,
      }),
      providesTags: [{ type: 'Attendance', id: 'ACTIVE' }],
    }),

    // Check in
    checkIn: builder.mutation<Attendance, CheckInDto>({
      query: (data) => ({
        url: '/attendance/check-in',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: [
        { type: 'Attendance', id: 'LIST' },
        { type: 'Attendance', id: 'TODAY' },
        { type: 'Attendance', id: 'ACTIVE' },
      ],
    }),

    // Check out
    checkOut: builder.mutation<Attendance, { id: string; data: CheckOutDto }>({
      query: ({ id, data }) => ({
        url: `/attendance/check-out`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Attendance', id },
        { type: 'Attendance', id: 'LIST' },
        { type: 'Attendance', id: 'TODAY' },
        { type: 'Attendance', id: 'ACTIVE' },
      ],
    }),

    // Get attendance statistics
    getAttendanceStats: builder.query<AttendanceStats, { 
      farm_id?: string; 
      start_date?: string; 
      end_date?: string;
    }>({
      query: (params) => ({
        url: '/attendance/statistics',
        params,
      }),
    }),

    // Get attendance history
    getAttendanceHistory: builder.query<any[], {
      farmer_id?: string;
      date_from?: string;
      date_to?: string;
      limit?: number;
    }>({
      query: (params) => ({
        url: '/attendance/history',
        params,
      }),
      providesTags: [{ type: 'Attendance', id: 'HISTORY' }],
    }),
  }),
});

export const {
  useGetAttendancesQuery,
  useGetAttendanceQuery,
  useGetTodayAttendancesQuery,
  useGetActiveAttendancesQuery,
  useCheckInMutation,
  useCheckOutMutation,
  useGetAttendanceStatsQuery,
  useGetAttendanceHistoryQuery,
} = attendanceApi;