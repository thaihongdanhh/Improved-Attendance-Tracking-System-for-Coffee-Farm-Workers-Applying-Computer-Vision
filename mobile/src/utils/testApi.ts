// Test API connection utility
export const testApiConnection = async () => {
  const API_URL = 'http://sarm.n2nai.io:5100';
  
  console.log('🔍 Testing API connection...');
  console.log(`📡 API URL: ${API_URL}`);
  
  try {
    // Test root endpoint
    console.log('Testing root endpoint...');
    const rootResponse = await fetch(`${API_URL}/`);
    const rootData = await rootResponse.json();
    console.log('✅ Root endpoint response:', rootData);
    
    // Test health endpoint
    console.log('\nTesting health endpoint...');
    const healthResponse = await fetch(`${API_URL}/health`);
    const healthData = await healthResponse.json();
    console.log('✅ Health endpoint response:', healthData);
    
    // Test API v1 endpoint
    console.log('\nTesting API v1 farms endpoint...');
    const apiResponse = await fetch(`${API_URL}/api/v1/farms/`);
    const apiData = await apiResponse.json();
    console.log('✅ API v1 farms response:', apiData);
    
    // Test API v1 farmers endpoint
    console.log('\nTesting API v1 farmers endpoint...');
    const farmersResponse = await fetch(`${API_URL}/api/v1/farmers/`);
    const farmersData = await farmersResponse.json();
    console.log('✅ API v1 farmers response:', farmersData);
    
    console.log('\n🎉 API connection test completed successfully!');
    return true;
  } catch (error) {
    console.error('❌ API connection test failed:', error);
    return false;
  }
};