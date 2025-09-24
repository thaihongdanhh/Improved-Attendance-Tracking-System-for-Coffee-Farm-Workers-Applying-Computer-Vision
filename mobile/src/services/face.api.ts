import { baseApi } from './api';

export interface FaceEnrollmentResponse {
  success: boolean;
  message: string;
  farmer_id: string;
  face_id?: string;
  samples_collected: number;
  enrollment_complete: boolean;
}

export interface FaceVerifyResponse {
  verified: boolean;
  farmer_id?: string;
  farmer_name?: string;
  farm_id?: string;
  confidence?: number;
  message: string;
}

export interface FaceQualityResponse {
  face_detected: boolean;
  quality_score?: number;
  quality_details?: {
    overall_score: number;
    pose: {
      pitch: number;
      yaw: number;
      roll: number;
      is_frontal: boolean;
    };
    face_size: number;
    brightness?: number;
    sharpness?: number;
  };
  recommendations?: string[];
  message?: string;
}

export const faceApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    // Enroll face
    enrollFace: builder.mutation<FaceEnrollmentResponse, any>({
      query: (data) => ({
        url: '/face/enroll',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result) => 
        result?.farmer_id ? [{ type: 'Farmer', id: result.farmer_id }] : [],
    }),

    // Verify face
    verifyFace: builder.mutation<FaceVerifyResponse, { image: string }>({
      query: (data) => ({
        url: '/face/verify-json',
        method: 'POST',
        body: data,
      }),
    }),

    // Check face quality
    checkFaceQuality: builder.mutation<FaceQualityResponse, { image: string; expected_angle?: string }>({
      query: (data) => ({
        url: '/face/quality-json',
        method: 'POST',
        body: data,
      }),
    }),

    // Delete face enrollment
    deleteFaceEnrollment: builder.mutation<void, string>({
      query: (farmerId) => ({
        url: `/face/farmer/${farmerId}`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, farmerId) => [
        { type: 'Farmer', id: farmerId },
        { type: 'FaceEnrollment', id: farmerId },
      ],
    }),
  }),
});

export const {
  useEnrollFaceMutation,
  useVerifyFaceMutation,
  useCheckFaceQualityMutation,
  useDeleteFaceEnrollmentMutation,
} = faceApi;