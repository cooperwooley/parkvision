import { useState, useEffect } from 'react';
import { loginAdmin, initializeLot, getLotStatus, logout } from './services/api';
import LotVideo from "./components/LotVideo";
import SpatialParkingLotMap from './components/SpatialParkingLotMap';
import './App.css';


function App() {
  // View state (public dashboard or admin panel)
  const [view, setView] = useState<'public' | 'admin' | 'login'>('public');

  // Authentication state
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(
    localStorage.getItem('isLoggedIn') === 'true'
  );
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [loginError, setLoginError] = useState<string>('');

  // Lot initialization state
  const [lotName, setLotName] = useState<string>('');
  const [lotDescription, setLotDescription] = useState<string>('');
  const [lotAddress, setLotAddress] = useState<string>('');
  const [videoPath, setVideoPath] = useState<string>('');
  const [initError, setInitError] = useState<string>('');

  // Lot status state
  const [lotId, setLotId] = useState<number>(1); // Default to first lot
  const [lotStatus, setLotStatus] = useState<any>(null);
  const [statusError, setStatusError] = useState<string>('');

  // Check login status when component mounts
  useEffect(() => {
    if (isLoggedIn) {
      setView('admin');
    }
  }, [isLoggedIn]);

  // Handle login form submission
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    
    try {
      const message = await loginAdmin(username, password);
      setIsLoggedIn(true);
      setView('admin');
      alert(message); // Show success message
    } catch (error) {
      setLoginError(error instanceof Error ? error.message : 'Login failed');
    }
  };

  // Handle lot initialization
  const handleInitializeLot = async (e: React.FormEvent) => {
    e.preventDefault();
    setInitError('');
    
    try {
      const result = await initializeLot({
        name: lotName,
        description: lotDescription,
        address: lotAddress,
        video_path: videoPath
      });
      
      // Check the structure of the response from your actual API
      if (result.lot_id) {
        alert(`Lot initialized with ID: ${result.lot_id}`);
        setLotId(result.lot_id); // Update for status checking
      } else {
        alert('Lot initialized successfully');
      }
    } catch (error) {
      setInitError(error instanceof Error ? error.message : 'Initialization failed');
    }
  };

  // Handle logout - adapted to work even if server endpoint doesn't exist yet
  const handleLogout = () => {
    logout()
      setIsLoggedIn(false);
      setView('public');
  };

  // Navigate to login page
  const goToLogin = () => {
    setView('login');
  };

  // Navigate back to public view
  const goToPublic = () => {
    setView('public');
  };

  // Fetch lot status when lotId changes or periodically
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await getLotStatus(lotId);
        setLotStatus(status);
        setStatusError('');
      } catch (error) {
        setStatusError(error instanceof Error ? error.message : 'Failed to fetch status');
        setLotStatus(null);
      }
    };

    fetchStatus();
    
    // Set up periodic refresh every 5 seconds
    const intervalId = setInterval(fetchStatus, 5000);
    
    return () => clearInterval(intervalId);
  }, [lotId]);

  // Updated to handle the actual structure of lot status data from your API
  const renderParkingSpaces = () => {
    if (!lotStatus || !Array.isArray(lotStatus)) return null;
    
    return (
      <div className="spaces-grid">
        <SpatialParkingLotMap lotStatus={lotStatus} />
      </div>
    );
  };

  // Public dashboard view
  if (view === 'public') {
    return (
      <div className="parking-app">
        <header>
          <h1>ParkVision Dashboard</h1>
          <button onClick={goToLogin} className="admin-button">Admin Login</button>
        </header>

        <section className="public-lot-status">
          <h2>Current Parking Status</h2>
          <div className="lot-selector">
            <label>Select Parking Lot:</label>
            <input 
              type="number" 
              value={lotId} 
              onChange={(e) => setLotId(Number(e.target.value))}
              min="1" 
            />
          </div>
          
          {statusError && <div className="error">{statusError}</div>}
          
          {lotStatus && (
            <div className="status-display">
              <h3>{lotStatus.name || `Parking Lot #${lotId}`}</h3>
              
              {lotStatus.total_spaces !== undefined && (
                <div className="status-summary">
                  <div className="status-box">
                    <h4>Total Spaces</h4>
                    <div className="status-value">{lotStatus.total_spaces}</div>
                  </div>
                  <div className="status-box available-box">
                    <h4>Available</h4>
                    <div className="status-value">{lotStatus.available_spaces || 'N/A'}</div>
                  </div>
                  <div className="status-box occupied-box">
                    <h4>Occupied</h4>
                    <div className="status-value">{lotStatus.occupied_spaces || 'N/A'}</div>
                  </div>
                </div>
              )}
              
              {lotStatus.last_updated && (
                <p className="update-time">Last Updated: {new Date(lotStatus.last_updated).toLocaleString()}</p>
              )}
              
              <h3>Parking Space Map</h3>
              {renderParkingSpaces()}
            </div>
          )}
        </section>
        
        <footer>
          <p>© 2025 ParkVision Management System</p>
        </footer>
      </div>
    );
  }

  // Login view
  if (view === 'login') {
    return (
      <div className="login-page">
        <div className="login-container">
          <button onClick={goToPublic} className="back-button">← Back to Dashboard</button>
          <h2>Admin Login</h2>
          <form onSubmit={handleLogin}>
            <div>
              <label>Username/Email:</label>
              <input 
                type="text" 
                value={username} 
                onChange={(e) => setUsername(e.target.value)}
                required 
              />
            </div>
            <div>
              <label>Password:</label>
              <input 
                type="password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)}
                required 
              />
            </div>
            {loginError && <div className="error">{loginError}</div>}
            <button type="submit" className="login-button">Login</button>
          </form>
        </div>
      </div>
    );
  }

  // Admin view (when logged in)
  return (
    <div className="parking-app admin-view">
      <header>
        <h1>ParkVision Management System</h1>
        <div className="header-buttons">
          <button onClick={goToPublic} className="view-public-button">View Public Dashboard</button>
          <button onClick={handleLogout} className="logout-button">Logout</button>
        </div>
      </header>

      <section className="init-lot">
        <h2>Initialize New Parking Lot</h2>
        <form onSubmit={handleInitializeLot}>
          <div>
            <label>Name:</label>
            <input 
              type="text" 
              value={lotName} 
              onChange={(e) => setLotName(e.target.value)}
              required 
            />
          </div>
          <div>
            <label>Description:</label>
            <input 
              type="text" 
              value={lotDescription} 
              onChange={(e) => setLotDescription(e.target.value)}
            />
          </div>
          <div>
            <label>Address:</label>
            <input 
              type="text" 
              value={lotAddress} 
              onChange={(e) => setLotAddress(e.target.value)}
            />
          </div>
          <div>
            <label>Video Path:</label>
            <input 
              type="text" 
              value={videoPath} 
              onChange={(e) => setVideoPath(e.target.value)}
              required 
              placeholder="Path to video file for parking spot detection"
            />
          </div>
          {initError && <div className="error">{initError}</div>}
          <button type="submit">Initialize Lot</button>
        </form>
      </section>

      <section className="lot-status">
        <h2>Lot Status</h2>
        <div>
          <label>Lot ID:</label>
          <input 
            type="number" 
            value={lotId} 
            onChange={(e) => setLotId(Number(e.target.value))}
            min="1" 
          />
        </div>
        {statusError && <div className="error">{statusError}</div>}
        {lotStatus && (
          <div className="status-display">
            <h3>{lotStatus.name || `Parking Lot #${lotId}`}</h3>
            
            {lotStatus.total_spaces !== undefined && (
              <>
                <p>Total Spaces: {lotStatus.total_spaces}</p>
                <p>Available Spaces: {lotStatus.available_spaces || 'N/A'}</p>
                <p>Occupied Spaces: {lotStatus.occupied_spaces || 'N/A'}</p>
              </>
            )}
            
            {lotStatus.last_updated && (
              <p>Last Updated: {new Date(lotStatus.last_updated).toLocaleString()}</p>
            )}
            
            {renderParkingSpaces()}
          </div>
        )}
        
        <LotVideo />
      </section>
    </div>
  );
}

export default App;