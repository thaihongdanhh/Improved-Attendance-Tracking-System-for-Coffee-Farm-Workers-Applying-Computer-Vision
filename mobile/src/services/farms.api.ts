import { baseApi } from './api';

export interface Farm {
  id: string;
  farm_code: string;
  farm_name: string;
  location?: {
    lat: number;
    lng: number;
  };
  address?: string;
  area_hectares?: number;
  manager_name?: string;
  contact_phone?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateFarmDto {
  farm_code: string;
  farm_name: string;
  location?: {
    lat: number;
    lng: number;
  };
  address?: string;
  area_hectares?: number;
  manager_name?: string;
  contact_phone?: string;
}

export interface UpdateFarmDto extends Partial<CreateFarmDto> {
  is_active?: boolean;
}

export interface FarmStatistics {
  total_farmers: number;
  active_farmers: number;
  total_attendances_today: number;
  total_attendances_month: number;
  average_work_hours: number;
}

export const farmsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    // Get all farms
    getFarms: builder.query<Farm[], { skip?: number; limit?: number }>({
      query: (params) => ({
        url: '/farms',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Farm' as const, id })),
              { type: 'Farm', id: 'LIST' },
            ]
          : [{ type: 'Farm', id: 'LIST' }],
    }),

    // Get farm by ID
    getFarm: builder.query<Farm, string>({
      query: (id) => `/farms/${id}`,
      providesTags: (result, error, id) => [{ type: 'Farm', id }],
    }),

    // Create farm
    createFarm: builder.mutation<Farm, CreateFarmDto>({
      query: (farm) => ({
        url: '/farms',
        method: 'POST',
        body: farm,
      }),
      invalidatesTags: [{ type: 'Farm', id: 'LIST' }],
    }),

    // Update farm
    updateFarm: builder.mutation<Farm, { id: string; data: UpdateFarmDto }>({
      query: ({ id, data }) => ({
        url: `/farms/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Farm', id },
        { type: 'Farm', id: 'LIST' },
      ],
    }),

    // Delete farm
    deleteFarm: builder.mutation<void, string>({
      query: (id) => ({
        url: `/farms/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'Farm', id },
        { type: 'Farm', id: 'LIST' },
      ],
    }),

    // Get farm statistics
    getFarmStatistics: builder.query<FarmStatistics, string>({
      query: (farmId) => `/farms/${farmId}/statistics`,
      providesTags: (result, error, id) => [{ type: 'Farm', id }],
    }),
  }),
});

export const {
  useGetFarmsQuery,
  useGetFarmQuery,
  useCreateFarmMutation,
  useUpdateFarmMutation,
  useDeleteFarmMutation,
  useGetFarmStatisticsQuery,
} = farmsApi;