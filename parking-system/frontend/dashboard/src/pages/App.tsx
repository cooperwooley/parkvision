import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './Dashboard'; // Ensure Dashboard is imported
import LoginPage from './LoginPage';
import InitializeLotPage from './InitializeLotPage';
import '../App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/initialize-lot" element={<InitializeLotPage />} />
        <Route path="*" element={<Navigate to="/" />} /> {/* Redirect to Dashboard for unknown routes */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
