import { useState } from 'react';
import LotInitializationForm from './LotInitializationForm';
import parkingApi from '../services/api';

interface AdminPanelProps {
  onLogout: () => void;
  onLotSelect: (lotId: number) => void;
}

const AdminPanel: React.FC<AdminPanelProps> = ({ onLogout, onLotSelect }) => {
  const [showInitForm, setShowInitForm] = useState(false);

  const handleLogout = () => {
    parkingApi.logout();
    onLogout();
  };

  const handleInitSuccess = (lotId: number) => {
    setShowInitForm(false);
    onLotSelect(lotId);
  };

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h2>Administrator Panel</h2>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </div>

      <div className="admin-controls">
        <button 
          onClick={() => setShowInitForm(!showInitForm)}
          className="control-btn"
        >
          {showInitForm ? 'Hide Form' : 'Initialize New Lot'}
        </button>
      </div>

      {showInitForm && (
        <LotInitializationForm onInitSuccess={handleInitSuccess} />
      )}

      <div className="admin-actions">
        <h3>Quick Actions</h3>
        <div className="action-buttons">
          <button onClick={() => onLotSelect(1)}>View Lot #1</button>
          {/* You can add more quick actions here */}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;