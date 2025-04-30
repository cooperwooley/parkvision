import { useState } from 'react';
import './App.css';

// Define TypeScript interfaces
interface ParkingSpot {
  id: number;
  status: 'occupied' | 'available';
  x: number;
  y: number;
}

function App() {
  const [spots, setSpots] = useState<ParkingSpot[]>([
    { id: 1, status: 'occupied', x: 85, y: 105 },
    { id: 2, status: 'available', x: 114, y: 105 },
    { id: 3, status: 'available', x: 142, y: 105 }
  ]);

  const totalSpots = spots.length;
  const availableCount = spots.filter(spot => spot.status === 'available').length;
  const lastUpdated = new Date().toLocaleTimeString();

  const handleRefresh = () => {
    // Later, replace with real API call
    alert('Refreshing data...');
  };

  return (
    <div className="dashboard">
      <h1>🚗 ParkVision Dashboard</h1>
      
      <div className="parking-container">
        <img src="/lot.png" alt="Parking Lot" className="lot-image" />
        <div className="spots-overlay">
          {spots.map((spot) => (
            <div
              key={spot.id}
              className={`spot ${spot.status}`}
              style={{ left: spot.x, top: spot.y }}
            ></div>
          ))}
        </div>
      </div>

      <div className="info-panel">
        <p><strong>🅿️ {availableCount}</strong> spots available / {totalSpots} total</p>
        <p>🕒 Last updated: {lastUpdated}</p>
        <button onClick={handleRefresh}>🔄 Refresh</button>
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
  );
}

export default App;