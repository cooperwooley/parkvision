import { useState } from 'react';
import { initializeLot } from '../services/api';

export default function InitializeLotPage() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [address, setAddress] = useState('');
  const [videoPath, setVideoPath] = useState('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    try {
      const res = await initializeLot({ name, description, address, video_path: videoPath });
      setResult(res);
      setError('');
    } catch (err: any) {
      setError(err.message);
      setResult(null);
    }
  };

  return (
    <div className="p-4 max-w-lg mx-auto">
      <h1 className="text-xl font-semibold mb-4">Initialize Parking Lot</h1>
      <input
        className="block w-full mb-2 p-2 border rounded"
        placeholder="Lot Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <input
        className="block w-full mb-2 p-2 border rounded"
        placeholder="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      <input
        className="block w-full mb-2 p-2 border rounded"
        placeholder="Address (optional)"
        value={address}
        onChange={(e) => setAddress(e.target.value)}
      />
      <input
        className="block w-full mb-2 p-2 border rounded"
        placeholder="Video Path"
        value={videoPath}
        onChange={(e) => setVideoPath(e.target.value)}
      />
      <button onClick={handleSubmit} className="bg-blue-600 text-white px-4 py-2 rounded">
        Submit
      </button>

      {error && <p className="text-red-600 mt-2">{error}</p>}
      {result && (
        <div className="mt-4 p-2 border rounded bg-gray-100">
          <p><strong>Lot ID:</strong> {result.lot_id}</p>
          <p><strong>Spots detected:</strong> {result.spots.length}</p>
        </div>
      )}
    </div>
  );
}
