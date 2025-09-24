import { baseApi } from './api';

export interface Farmer {
  id: string;
  farmer_code: string;
  full_name: string;
  phone?: string;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other';
  address?: string;
  farm_id: string;
  is_active: boolean;
  face_enrolled: boolean;
  face_samples_count: number;
  last_attendance?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateFarmerDto {
  farmer_code: string;
  full_name: string;
  phone?: string;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other';
  address?: string;
  farm_id: string;
}

export interface UpdateFarmerDto extends Partial<CreateFarmerDto> {
  is_active?: boolean;
}

export const farmersApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    // Get all farmers
    getFarmers: builder.query<Farmer[], { skip?: number; limit?: number; farm_id?: string }>({
      query: (params) => ({
        url: '/farmers/',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Farmer' as const, id })),
              { type: 'Farmer', id: 'LIST' },
            ]
          : [{ type: 'Farmer', id: 'LIST' }],
    }),

    // Get farmer by ID
    getFarmer: builder.query<Farmer, string>({
      query: (id) => `/farmers/${id}`,
      providesTags: (result, error, id) => [{ type: 'Farmer', id }],
    }),

    // Create farmer
    createFarmer: builder.mutation<Farmer, CreateFarmerDto>({
      query: (farmer) => ({
        url: '/farmers/',
        method: 'POST',
        body: farmer,
      }),
      invalidatesTags: [{ type: 'Farmer', id: 'LIST' }],
    }),

    // Update farmer
    updateFarmer: builder.mutation<Farmer, { id: string; data: UpdateFarmerDto }>({
      query: ({ id, data }) => ({
        url: `/farmers/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Farmer', id },
        { type: 'Farmer', id: 'LIST' },
      ],
    }),

    // Delete farmer
    deleteFarmer: builder.mutation<void, string>({
      query: (id) => ({
        url: `/farmers/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'Farmer', id },
        { type: 'Farmer', id: 'LIST' },
      ],
    }),

    // Get farmer's face embeddings
    getFarmerEmbeddings: builder.query<any[], string>({
      query: (farmerId) => `/farmers/${farmerId}/embeddings`,
      providesTags: (result, error, id) => [{ type: 'FaceEnrollment', id }],
    }),

    // Get farmer's attendance history
    getFarmerAttendances: builder.query<{
      farmer_id: string;
      farmer_name: string;
      from_date: string;
      to_date: string;
      total_records: number;
      limit: number;
      offset: number;
      attendances: any[];
    }, string>({
      query: (farmerId) => `/farmers/${farmerId}/attendances`,
      providesTags: ['Attendance'],
    }),
  }),
});

export const {
  useGetFarmersQuery,
  useGetFarmerQuery,
  useCreateFarmerMutation,
  useUpdateFarmerMutation,
  useDeleteFarmerMutation,
  useGetFarmerEmbeddingsQuery,
  useGetFarmerAttendancesQuery,
} = farmersApi;