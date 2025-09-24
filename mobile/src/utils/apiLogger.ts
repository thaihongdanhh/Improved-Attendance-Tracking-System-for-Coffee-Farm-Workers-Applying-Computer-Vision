// API Logger utility for debugging
export const apiLogger = {
  request: (endpoint: string, method: string, data?: any) => {
    console.log(`🚀 API Request: ${method} ${endpoint}`);
    if (data) {
      console.log('📦 Request Data:', data);
    }
  },
  
  response: (endpoint: string, status: number, data?: any) => {
    if (status >= 200 && status < 300) {
      console.log(`✅ API Response: ${endpoint} - Status: ${status}`);
    } else {
      console.log(`❌ API Error: ${endpoint} - Status: ${status}`);
    }
    if (data) {
      console.log('📥 Response Data:', data);
    }
  },
  
  error: (endpoint: string, error: any) => {
    console.error(`🔥 API Error: ${endpoint}`, error);
  }
};