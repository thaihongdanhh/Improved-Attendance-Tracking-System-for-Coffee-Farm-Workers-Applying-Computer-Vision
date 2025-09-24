export const testCreateFarmer = async () => {
  const API_URL = 'http://sarm.n2nai.io:5100/api/v1/farmers/';
  
  const testData = {
    farmer_code: 'BT9999',
    full_name: 'Test Direct API',
    gender: 'male',
    farm_id: 'default_farm'
  };
  
  console.log('Testing direct API call...');
  console.log('URL:', API_URL);
  console.log('Data:', testData);
  
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testData),
    });
    
    console.log('Response status:', response.status);
    console.log('Response headers:', response.headers);
    
    const data = await response.json();
    console.log('Response data:', data);
    
    return data;
  } catch (error) {
    console.error('Direct API call failed:', error);
    throw error;
  }
};