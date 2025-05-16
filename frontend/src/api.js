// frontend/src/api.js
import axios from 'axios'

// Configure the base URL for your backend API
// Assuming your backend is running on localhost:8001 as per the last error
// and the API router has a prefix of "/api"
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
    // You might add headers for authentication here later, e.g., 'Authorization': 'Bearer YOUR_TOKEN'
  },
})

// Optional: Add request or response interceptors for logging, error handling, etc.
// apiClient.interceptors.request.use(request => {
//   console.log('Starting Request', request);
//   return request;
// });

// apiClient.interceptors.response.use(response => {
//   console.log('Response:', response);
//   return response;
// }, error => {
//   console.error('API Error:', error.response || error.message);
//   // Handle specific errors or re-throw
//   return Promise.reject(error);
// });

export default apiClient
