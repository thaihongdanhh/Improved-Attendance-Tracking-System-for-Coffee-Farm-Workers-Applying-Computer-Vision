import { baseApi } from './api';

export interface CoffeeBeansAnalysis {
  id: string;
  analysis: {
    total_beans: number;
    good_beans: number;
    defect_beans: number;
    quality_score: number;
    defects_breakdown?: {
      [key: string]: number;
    };
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
  is_video?: boolean;
}

export const coffeeBeansApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    analyzeCoffeeBeans: builder.mutation<CoffeeBeansAnalysis, FormData>({
      query: (formData) => ({
        url: '/coffee-beans/analyze',
        method: 'POST',
        body: formData,
      }),
      invalidatesTags: ['Farmer'],
    }),
    getCoffeeBeansHistory: builder.query<CoffeeBeansAnalysis[], void>({
      query: () => '/coffee-beans/history',
      providesTags: ['Farmer'],
    }),
    getCoffeeBeansAnalysis: builder.query<CoffeeBeansAnalysis, string>({
      query: (id) => `/coffee-beans/${id}`,
      providesTags: ['Farmer'],
    }),
  }),
});

export const {
  useAnalyzeCoffeeBeansMutation,
  useGetCoffeeBeansHistoryQuery,
  useGetCoffeeBeansAnalysisQuery,
} = coffeeBeansApi;