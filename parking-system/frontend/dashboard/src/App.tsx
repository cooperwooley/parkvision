import { useState, useEffect } from 'react';
import AdminLogin from './components/AdminLogin';
import AdminPanel from './components/AdminPanel';
import parkingApi, { ParkingSpot as ApiParkingSpot, ParkingLot } from './services/api';
import './App.css';

// Interface for our frontend spot representation
interface SpotDisplay {
  id: number;
  status: 'occupied' | 'available';
  x: number;
  y: number;
  width: number;
  height: number;
}

function App() {
  const [spots, setSpots] = useState<SpotDisplay[]>([]);
  const [lotInfo, setLotInfo] = useState<Partial<ParkingLot>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>(new Date().toLocaleTimeString());
  const [isAdmin, setIsAdmin] = useState<boolean>(parkingApi.isLoggedIn());
  const [lotId, setLotId] = useState<number>(1); // Default to lot ID 1
  const [showAdminPanel, setShowAdminPanel] = useState<boolean>(false);

  // Convert API status to our display status
  const mapStatus = (apiStatus: 'empty' | 'occupied'): 'available' | 'occupied' => {
    return apiStatus === 'empty' ? 'available' : 'occupied';
  };
  
  // Convert API spots to our display format
  const mapApiSpotsToDisplay = (apiSpots: ApiParkingSpot[]): SpotDisplay[] => {
    return apiSpots.map(spot => ({
      id: spot.id,
      status: mapStatus(spot.status),
      x: spot.x,
      y: spot.y,
      width: spot.width,
      height: spot.height
    }));
  };

  // Fetch lot status on component mount and at intervals
  useEffect(() => {
    const fetchLotStatus = async () => {
      try {
        setLoading(true);
        const lotData = await parkingApi.getLotStatus(lotId);
        setLotInfo({
          lot_id: lotData.lot_id,
          name: lotData.name,
          description: lotData.description,
          address: lotData.address
        });
        setSpots(mapApiSpotsToDisplay(lotData.spots));
        setLastUpdated(new Date().toLocaleTimeString());
        setError(null);
      } catch (err) {
        console.error('Error fetching lot status:', err);
        setError('Failed to load parking data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    // Fetch initially
    fetchLotStatus();

    // Then set up polling every 10 seconds
    const intervalId = setInterval(fetchLotStatus, 10000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, [lotId]);

  const handleRefresh = async () => {
    try {
      setLoading(true);
      const lotData = await parkingApi.getLotStatus(lotId);
      setSpots(mapApiSpotsToDisplay(lotData.spots));
      setLastUpdated(new Date().toLocaleTimeString());
      setError(null);
    } catch (err) {
      console.error('Error refreshing data:', err);
      setError('Failed to refresh parking data');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSuccess = () => {
    setIsAdmin(true);
    setShowAdminPanel(true);
  };

  const handleLogout = () => {
    setIsAdmin(false);
    setShowAdminPanel(false);
  };

  const handleLotSelect = (newLotId: number) => {
    setLotId(newLotId);
    setShowAdminPanel(false); // Hide admin panel when switching lots
  };

  const totalSpots = spots.length;
  const availableCount = spots.filter(spot => spot.status === 'available').length;

  return (
    <div className="app-container">
      <div className="dashboard">
        <div className="header-row">
          <h1>🚗 ParkVision Dashboard</h1>
          {isAdmin && (
            <button 
              onClick={() => setShowAdminPanel(!showAdminPanel)} 
              className="admin-toggle-btn"
            >
              {showAdminPanel ? 'Hide Admin Panel' : 'Show Admin Panel'}
            </button>
          )}
          {!isAdmin && (
            <button 
              onClick={() => setShowAdminPanel(true)}
              className="admin-login-btn"
            >
              Admin Login
            </button>
          )}
        </div>
        
        {showAdminPanel && !isAdmin && (
          <AdminLogin onLoginSuccess={handleLoginSuccess} />
        )}
        
        {showAdminPanel && isAdmin && (
          <AdminPanel onLogout={handleLogout} onLotSelect={handleLotSelect} />
        )}

        {!showAdminPanel && (
          <div className="parking-view">
            {lotInfo.name && (
              <div className="lot-header">
                <h2>{lotInfo.name}</h2>
                <p>{lotInfo.description} • {lotInfo.address}</p>
              </div>
            )}
            
            {loading && <div className="loading">Loading parking data...</div>}
            {error && <div className="error-message">{error}</div>}
            
            <div className="parking-container">
              <img src="/lot.png" alt="Parking Lot" className="lot-image" />
              <div className="spots-overlay">
                {spots.map((spot) => (
                  <div
                    key={spot.id}
                    className={`spot ${spot.status}`}
                    style={{ 
                      left: spot.x, 
                      top: spot.y,
                      width: spot.width,
                      height: spot.height
                    }}
                  ></div>
                ))}
              </div>
            </div>

            <div className="info-panel">
              <p><strong>🅿️ {availableCount}</strong> spots available / {totalSpots} total</p>
              <p>🕒 Last updated: {lastUpdated}</p>
              <button onClick={handleRefresh} disabled={loading}>
                {loading ? 'Refreshing...' : '🔄 Refresh'}
              </button>
            </div>

            <div className="legend">
              <div className="legend-item">
                <div className="legend-box occupied"></div> Occupied
              </div>
              <div className="legend-item">
                <div className="legend-box available"></div> Available
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;