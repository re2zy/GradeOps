import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import Navbar from './components/Navbar'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import UploadPage from './pages/UploadPage'
import ReviewPage from './pages/ReviewPage'

function PrivateRoute({ children }) {
  const token = useSelector((s) => s.auth.token)
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  const token = useSelector((s) => s.auth.token)
  return (
    <>
      {token && <Navbar />}
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<PrivateRoute><DashboardPage /></PrivateRoute>} />
        <Route path="/upload/:examId" element={<PrivateRoute><UploadPage /></PrivateRoute>} />
        <Route path="/review/:examId" element={<PrivateRoute><ReviewPage /></PrivateRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}
