import { Link, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { logout } from '../store'

export default function Navbar() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const user = useSelector((s) => s.auth.user)

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
  }

  return (
    <nav style={S.nav}>
      <Link to="/" style={S.brand}>GradeOps</Link>
      <div style={S.right}>
        <span style={S.user}>{user?.full_name} · {user?.role}</span>
        <button onClick={handleLogout} style={S.btn}>Logout</button>
      </div>
    </nav>
  )
}

const S = {
  nav: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 28px', background: '#12122a', borderBottom: '1px solid #222' },
  brand: { color: '#e94560', fontWeight: 700, fontSize: 20 },
  right: { display: 'flex', gap: 16, alignItems: 'center' },
  user: { fontSize: 13, color: '#888' },
  btn: { background: '#e94560', color: '#fff', border: 'none', padding: '6px 14px', borderRadius: 6, cursor: 'pointer', fontSize: 13 },
}
