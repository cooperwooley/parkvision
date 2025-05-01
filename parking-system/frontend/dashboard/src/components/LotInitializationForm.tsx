import { useState } from 'react';
import parkingApi from '../services/api';

interface LotInitFormProps {
  onInitSuccess: (lotId: number) => void;
}

const LotInitializationForm: React.FC<LotInitFormProps> = ({ onInitSuccess }) => {
  const [videoPath, setVideoPath] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [address, setAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const result = await parkingApi.initializeLot(videoPath, name, description, address);
      onInitSuccess(result.lot_id);
    } catch (err: any) {
      console.error('Error initializing lot:', err);
      setError(err.response?.data?.message || 'Failed to initialize parking lot. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="lot-init-form">
      <h2>Initialize New Parking Lot</h2>
      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="videoPath">Video File Path</label>
          <input
            type="text"
            id="videoPath"
            value={videoPath}
            onChange={(e) => setVideoPath(e.target.value)}
            placeholder="/path/to/video.mp4"
            required
          />
          <small>Path to the video file for spot detection</small>
        </div>

        <div className="form-group">
          <label htmlFor="name">Lot Name</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., North Campus Lot"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <input
            type="text"
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g., Near Engineering Hall"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="address">Address</label>
          <input
            type="text"
            id="address"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="e.g., 123 Main St"
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Initializing...' : 'Initialize Lot'}
        </button>
      </form>
    </div>
  );
};

export default LotInitializationForm;