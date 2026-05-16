import { useEffect, useState, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { fetchPendingGrades, fetchReviewStats, submitReview, nextGrade, prevGrade } from '../store'

export default function ReviewPage() {
  const { examId } = useParams()
  const dispatch = useDispatch()
  const { pendingGrades, currentIndex, stats, loading } = useSelector((s) => s.grades)
  const [showOverride, setShowOverride] = useState(false)
  const [overrideScore, setOverrideScore] = useState('')
  const [overrideComment, setOverrideComment] = useState('')

  const grade = pendingGrades[currentIndex]

  useEffect(() => {
    dispatch(fetchPendingGrades(Number(examId)))
    dispatch(fetchReviewStats(Number(examId)))
  }, [dispatch, examId])

  const handleApprove = useCallback(() => {
    if (!grade) return
    dispatch(submitReview({ gradeId: grade.id, action: 'approve' }))
    dispatch(fetchReviewStats(Number(examId)))
  }, [grade, dispatch, examId])

  const handleOverrideSubmit = useCallback(() => {
    if (!grade || overrideScore === '') return
    dispatch(submitReview({ gradeId: grade.id, action: 'override', score: Number(overrideScore), comment: overrideComment }))
    dispatch(fetchReviewStats(Number(examId)))
    setShowOverride(false)
    setOverrideScore('')
    setOverrideComment('')
  }, [grade, overrideScore, overrideComment, dispatch, examId])

  useEffect(() => {
    const onKey = (e) => {
      if (showOverride) { if (e.key === 'Escape') setShowOverride(false); return }
      if (e.key === 'a' || e.key === 'A') handleApprove()
      if (e.key === 'o' || e.key === 'O') setShowOverride(true)
      if (e.key === 'ArrowRight' || e.key === 'n') dispatch(nextGrade())
      if (e.key === 'ArrowLeft'  || e.key === 'p') dispatch(prevGrade())
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [handleApprove, dispatch, showOverride])

  if (loading) return <div style={S.center}><p style={{ color: '#555' }}>Loading grades…</p></div>
  if (!grade) return (
    <div style={S.center}>
      <p style={{ color: '#10b981', fontSize: 18, fontWeight: 600 }}>All grades reviewed!</p>
      {stats && <p style={{ color: '#555', marginTop: 8 }}>Approved: {stats.approved} · Overridden: {stats.overridden}</p>}
    </div>
  )

  return (
    <div style={S.page}>
      {/* Stats bar */}
      <div style={S.statsBar}>
        {stats && <>
          <span style={S.stat}>{stats.pending} pending</span>
          <span style={{ ...S.stat, color: '#10b981' }}>{stats.approved} approved</span>
          <span style={{ ...S.stat, color: '#f59e0b' }}>{stats.overridden} overridden</span>
          {stats.plagiarism_flagged > 0 && <span style={{ ...S.stat, color: '#e94560' }}>{stats.plagiarism_flagged} flagged</span>}
          <div style={S.bar}><div style={{ ...S.fill, width: `${stats.progress_pct}%` }} /></div>
          <span style={S.stat}>{stats.progress_pct}%</span>
        </>}
      </div>

      {/* Main card */}
      <div style={S.card}>
        <div style={S.cardTop}>
          <span style={S.qLabel}>Q{grade.question_number}</span>
          {grade.plagiarism_flagged && <span style={S.plagBadge}>Plagiarism Flagged</span>}
          <div style={S.navWrap}>
            <button style={S.navBtn} onClick={() => dispatch(prevGrade())}>← Prev</button>
            <span style={{ color: '#555', fontSize: 13 }}>{currentIndex + 1} / {pendingGrades.length}</span>
            <button style={S.navBtn} onClick={() => dispatch(nextGrade())}>Next →</button>
          </div>
        </div>

        <p style={S.qText}>{grade.question_text}</p>

        <div style={S.split}>
          {/* Left: student image */}
          <div style={S.imgPane}>
            {grade.cropped_image_url
              ? <img src={grade.cropped_image_url} alt="Student answer" style={S.img} />
              : <span style={{ color: '#333', fontSize: 13 }}>No image available</span>
            }
          </div>

          {/* Right: AI grade details */}
          <div style={S.detailPane}>
            <div style={S.scoreBox}>
              <span style={{ color: '#888', fontSize: 13 }}>AI Score</span>
              <span style={{ color: '#fff', fontWeight: 700, fontSize: 22 }}>{grade.ai_score} / {grade.max_score}</span>
            </div>
            <div style={S.box}>
              <p style={S.boxLabel}>Justification</p>
              <p style={{ color: '#ccc', fontSize: 13, lineHeight: 1.7 }}>{grade.justification}</p>
            </div>
            {grade.plagiarism_note && (
              <div style={S.plagBox}><strong>Plagiarism:</strong> {grade.plagiarism_note}</div>
            )}
            <div style={S.box}>
              <p style={S.boxLabel}>Extracted Answer</p>
              <p style={{ color: '#aaa', fontSize: 12, fontFamily: 'monospace', lineHeight: 1.6 }}>
                {grade.extracted_answer || '(none)'}
              </p>
            </div>
          </div>
        </div>

        <div style={S.actionRow}>
          <button style={S.approveBtn} onClick={handleApprove}>Approve <kbd style={S.kbd}>A</kbd></button>
          <button style={S.overrideBtn} onClick={() => setShowOverride(true)}>Override <kbd style={S.kbd}>O</kbd></button>
        </div>
        <p style={{ color: '#333', fontSize: 11, textAlign: 'center', marginTop: 8 }}>
          <kbd style={S.kbd}>←</kbd> <kbd style={S.kbd}>→</kbd> navigate &nbsp; <kbd style={S.kbd}>Esc</kbd> close modal
        </p>
      </div>

      {/* Override modal */}
      {showOverride && (
        <div style={S.overlay} onClick={() => setShowOverride(false)}>
          <div style={S.modal} onClick={(e) => e.stopPropagation()}>
            <h3 style={{ color: '#fff', marginBottom: 4 }}>Override Score</h3>
            <p style={{ color: '#666', fontSize: 13, marginBottom: 16 }}>AI gave {grade.ai_score} / {grade.max_score}</p>
            <input autoFocus style={S.input} type="number" placeholder={`Score (0–${grade.max_score})`}
              min={0} max={grade.max_score} step={0.5}
              value={overrideScore} onChange={(e) => setOverrideScore(e.target.value)} />
            <textarea style={{ ...S.input, minHeight: 80, marginTop: 8 }} placeholder="Comment (optional)"
              value={overrideComment} onChange={(e) => setOverrideComment(e.target.value)} />
            <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
              <button style={{ ...S.approveBtn, flex: 1 }} onClick={handleOverrideSubmit}>Submit Override</button>
              <button style={{ ...S.overrideBtn, flex: 1, background: '#222' }} onClick={() => setShowOverride(false)}>
                Cancel <kbd style={S.kbd}>Esc</kbd>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const S = {
  page: { maxWidth: 1100, margin: '32px auto', padding: '0 24px' },
  center: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' },
  statsBar: { display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20, background: '#1a1a2e', padding: '10px 18px', borderRadius: 8 },
  stat: { color: '#aaa', fontSize: 13 },
  bar: { flex: 1, height: 6, background: '#2a2a3e', borderRadius: 3 },
  fill: { height: '100%', background: '#10b981', borderRadius: 3, transition: 'width .3s' },
  card: { background: '#1a1a2e', borderRadius: 12, padding: 24 },
  cardTop: { display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 },
  qLabel: { color: '#e94560', fontWeight: 700, fontSize: 18 },
  plagBadge: { background: '#e94560', color: '#fff', fontSize: 11, padding: '3px 8px', borderRadius: 4 },
  navWrap: { display: 'flex', alignItems: 'center', gap: 8, marginLeft: 'auto' },
  navBtn: { background: '#16213e', color: '#aaa', border: 'none', padding: '5px 12px', borderRadius: 5, cursor: 'pointer', fontSize: 13 },
  qText: { color: '#ddd', fontSize: 15, marginBottom: 18 },
  split: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 },
  imgPane: { background: '#0f0f1a', borderRadius: 8, minHeight: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' },
  img: { width: '100%', height: '100%', objectFit: 'contain' },
  detailPane: { display: 'flex', flexDirection: 'column', gap: 12 },
  scoreBox: { background: '#16213e', borderRadius: 8, padding: '12px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  box: { background: '#16213e', borderRadius: 8, padding: '12px 16px', flex: 1 },
  boxLabel: { color: '#555', fontSize: 11, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6 },
  plagBox: { background: '#1a0a0a', border: '1px solid #e94560', borderRadius: 6, padding: '8px 12px', color: '#f88', fontSize: 13 },
  actionRow: { display: 'flex', gap: 12 },
  approveBtn: { flex: 1, padding: 12, background: '#10b981', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 700, fontSize: 16 },
  overrideBtn: { flex: 1, padding: 12, background: '#f59e0b', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 700, fontSize: 16 },
  kbd: { background: '#0f0f1a', color: '#888', padding: '1px 5px', borderRadius: 3, fontFamily: 'monospace', fontSize: 11 },
  overlay: { position: 'fixed', inset: 0, background: 'rgba(0,0,0,.75)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 },
  modal: { background: '#1a1a2e', borderRadius: 12, padding: 28, width: 420 },
  input: { padding: '9px 13px', borderRadius: 6, border: '1px solid #2a2a3e', background: '#0f0f1a', color: '#fff', fontSize: 14, width: '100%', outline: 'none' },
}
