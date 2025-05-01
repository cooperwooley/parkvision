import axios from 'axios';

// Define the base URL for your API
const API_BASE_URL = 'http://localhost:5000'; // Change this to your actual backend URL

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Define interfaces for API responses
export interface ParkingSpot {
  id: number;
  x: number;
  y: number;
  width: number;
  height: number;
  status: 'empty' | 'occupied';
}

export interface ParkingLot {
  lot_id: number;
  name: string;
  description: string;
  address: string;
  spots: ParkingSpot[];
}

// API service functions
export const parkingApi = {
  // Initialize a new parking lot
  initializeLot: async (videoPath: string, name: string, description: string, address: string) => {
    try {
      const response = await apiClient.post('/initialize_lot', {
        video_path: videoPath,
        name,
        description,
        address,
      });
      return response.data;
    } catch (error) {
      console.error('Error initializing lot:', error);
      throw error;
    }
  },

  // Get status of a specific lot
  getLotStatus: async (lotId: number): Promise<ParkingLot> => {
    try {
      const response = await apiClient.get(`/lot_status/${lotId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching status for lot ${lotId}:`, error);
      throw error;
    }
  },

  // Admin login
  adminLogin: async (username: string, password: string) => {
    try {
      const response = await apiClient.post('/admin/login', {
        username,
        password,
      });
      
      // Store the token if login is successful
      if (response.data.token) {
        localStorage.setItem('admin_token', response.data.token);
      }
      
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  // Logout (client-side only)
  logout: () => {
    localStorage.removeItem('admin_token');
  },

  // Check if user is logged in
  isLoggedIn: () => {
    return localStorage.getItem('admin_token') !== null;
  }
};

export default parkingApi;