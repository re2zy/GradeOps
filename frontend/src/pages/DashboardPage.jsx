import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { fetchExams } from '../store'

const STATUS_COLOR = { draft: '#555', active: '#1a73e8', grading: '#f59e0b', completed: '#10b981' }

export default function DashboardPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { list: exams, loading } = useSelector((s) => s.exams)
  const user = useSelector((s) => s.auth.user)

  useEffect(() => { dispatch(fetchExams()) }, [dispatch])

  return (
    <div style={S.page}>
      <div style={S.header}>
        <h2 style={S.h2}>Exams</h2>
        {user?.role === 'instructor' && (
          <button style={S.newBtn} onClick={() => navigate('/upload/new')}>+ New Exam</button>
        )}
      </div>

      {loading ? (
        <p style={S.muted}>Loading…</p>
      ) : exams.length === 0 ? (
        <p style={S.muted}>No exams yet.</p>
      ) : (
        <div style={S.grid}>
          {exams.map((exam) => (
            <div key={exam.id} style={S.card}>
              <h3 style={S.cardTitle}>{exam.title}</h3>
              <p style={S.cardSub}>{exam.course_code}</p>
              <span style={{ ...S.badge, background: STATUS_COLOR[exam.status] ?? '#555' }}>
                {exam.status}
              </span>
              <div style={S.actions}>
                {user?.role === 'instructor' && (
                  <button style={S.actionBtn} onClick={() => navigate(`/upload/${exam.id}`)}>
                    Upload Submissions
                  </button>
                )}
                <button style={{ ...S.actionBtn, background: '#16213e' }} onClick={() => navigate(`/review/${exam.id}`)}>
                  Review Grades
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

const S = {
  page: { maxWidth: 960, margin: '40px auto', padding: '0 24px' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 },
  h2: { color: '#fff', fontSize: 22 },
  newBtn: { background: '#e94560', color: '#fff', border: 'none', padding: '8px 18px', borderRadius: 6, cursor: 'pointer', fontWeight: 600 },
  muted: { color: '#555' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 },
  card: { background: '#1a1a2e', borderRadius: 10, padding: 20, display: 'flex', flexDirection: 'column', gap: 8 },
  cardTitle: { color: '#fff', fontSize: 15, fontWeight: 600 },
  cardSub: { color: '#666', fontSize: 13 },
  badge: { color: '#fff', fontSize: 11, padding: '3px 8px', borderRadius: 4, width: 'fit-content' },
  actions: { display: 'flex', gap: 8, marginTop: 4 },
  actionBtn: { flex: 1, padding: '7px 0', background: '#e94560', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 12 },
}
