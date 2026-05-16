import { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { login } from '../store'

export default function LoginPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { loading, error, token } = useSelector((s) => s.auth)
  const [form, setForm] = useState({ email: '', password: '' })

  useEffect(() => { if (token) navigate('/') }, [token, navigate])

  const handleSubmit = (e) => {
    e.preventDefault()
    dispatch(login(form))
  }

  return (
    <div style={S.page}>
      <div style={S.card}>
        <h1 style={S.title}>GradeOps</h1>
        <p style={S.sub}>AI-Powered Exam Grading</p>
        <form onSubmit={handleSubmit} style={S.form}>
          <input
            style={S.input} type="email" placeholder="Email" required
            value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <input
            style={S.input} type="password" placeholder="Password" required
            value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          {error && <p style={S.err}>{error}</p>}
          <button type="submit" style={S.btn} disabled={loading}>
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  )
}

const S = {
  page: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0f0f1a' },
  card: { background: '#1a1a2e', padding: 40, borderRadius: 12, width: 360, boxShadow: '0 4px 32px rgba(0,0,0,0.5)' },
  title: { color: '#e94560', margin: '0 0 4px', fontSize: 28, textAlign: 'center' },
  sub: { color: '#666', textAlign: 'center', marginBottom: 28, fontSize: 13 },
  form: { display: 'flex', flexDirection: 'column', gap: 12 },
  input: { padding: '10px 14px', borderRadius: 6, border: '1px solid #2a2a3e', background: '#0f0f1a', color: '#fff', fontSize: 14, outline: 'none' },
  err: { color: '#e94560', fontSize: 13, margin: 0 },
  btn: { padding: 11, borderRadius: 6, background: '#e94560', color: '#fff', border: 'none', fontSize: 15, cursor: 'pointer', fontWeight: 600 },
}
