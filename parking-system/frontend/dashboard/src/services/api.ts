const API_BASE_URL = 'http://localhost:5000'; // Flask default

// Login function with localStorage to track login status
export async function loginAdmin(username_or_email: string, password: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/admin/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // allows cookies/sessions to persist
    body: JSON.stringify({ username_or_email, password }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Login failed');
  }

  // Store login status in localStorage upon success
  localStorage.setItem('isLoggedIn', 'true');
  return data.message;
}

// Initialize parking lot with the provided form data
export async function initializeLot(form: {
  name: string;
  description?: string;
  address?: string;
  video_path: string;
}): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/initialize_lot`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(form),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Initialization failed');
  }

  return data;
}

// Fetch the status of a parking lot
export async function getLotStatus(lotId: number): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/lot_status/${lotId}`, {
    method: 'GET',
    credentials: 'include',
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Failed to fetch lot status');
  }

  return data;
}

// Log out function
export function logout() {
  // Remove login status from localStorage
  localStorage.removeItem('isLoggedIn');

  // Optionally, clear the session or cookie on the server side
  fetch(`${API_BASE_URL}/admin/logout`, {
    method: 'POST',
    credentials: 'include', // ensures the session cookie is sent
  }).then(response => {
    if (response.ok) {
      console.log('Logged out successfully');
    }
  });
}
