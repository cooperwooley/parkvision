import { useState } from 'react';
import { loginAdmin } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const msg = await loginAdmin(usernameOrEmail, password);
      setMessage(msg);
      setError('');
      // Redirect to the dashboard after a successful login
      navigate('/');  // Assuming '/' is the dashboard route
    } catch (err: any) {
      setError(err.message); // Display any errors (like invalid credentials)
      setMessage('');
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <input
        placeholder="Username or Email"
        value={usernameOrEmail}
        onChange={(e) => setUsernameOrEmail(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleLogin}>Login</button>
      {message && <p>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}
