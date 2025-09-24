import { baseApi } from './api';

export interface DiseaseDetection {
  disease: string;
  confidence: number;
  severity: string;
  bbox?: number[];
}

export interface CoffeeLeavesAnalysis {
  id: string;
  analysis: {
    total_leaves: number;
    healthy_leaves?: number;
    infected_leaves: number;
    health_score: number;
    diseases_detected: DiseaseDetection[];
    recommendations?: string[];
  };
  image_url: string;
  timestamp?: string;
  created_at: string;
  farm_id?: string;
  field_id?: string;
  notes?: string;
  filename?: string;
  user_id?: string;
}

export const coffeeLeavesApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    analyzeCoffeeLeaves: builder.mutation<CoffeeLeavesAnalysis, FormData>({
      query: (formData) => ({
        url: '/coffee-leaves/analyze',
        method: 'POST',
        body: formData,
      }),
      invalidatesTags: ['Farmer'],
    }),
    getCoffeeLeavesHistory: builder.query<CoffeeLeavesAnalysis[], void>({
      query: () => '/coffee-leaves/history',
      providesTags: ['Farmer'],
    }),
    getCoffeeLeavesAnalysis: builder.query<CoffeeLeavesAnalysis, string>({
      query: (id) => `/coffee-leaves/${id}`,
      providesTags: ['Farmer'],
    }),
  }),
});

export const {
  useAnalyzeCoffeeLeavesMutation,
  useGetCoffeeLeavesHistoryQuery,
  useGetCoffeeLeavesAnalysisQuery,
} = coffeeLeavesApi;