import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import api from '../api'

export default function UploadPage() {
  const { examId } = useParams()
  const navigate = useNavigate()
  const isNew = examId === 'new'

  const [examForm, setExamForm] = useState({ title: '', course_code: '', rubric: '' })
  const [createdExamId, setCreatedExamId] = useState(isNew ? null : Number(examId))
  const [rows, setRows] = useState([{ name: '', studentId: '', file: null }])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  const updateRow = (i, field, value) => {
    const next = [...rows]
    next[i] = { ...next[i], [field]: value }
    setRows(next)
  }

  const handleCreateExam = async (e) => {
    e.preventDefault()
    setError('')
    let rubric
    try { rubric = JSON.parse(examForm.rubric) } catch { setError('Rubric must be valid JSON'); return }
    try {
      const { data } = await api.post('/exams/', { ...examForm, rubric })
      setCreatedExamId(data.id)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create exam')
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!createdExamId) { setError('Create the exam first'); return }
    setUploading(true)
    setError('')
    try {
      const fd = new FormData()
      fd.append('student_names', JSON.stringify(rows.map((r) => r.name)))
      fd.append('student_ids', JSON.stringify(rows.map((r) => r.studentId)))
      rows.forEach((r) => fd.append('files', r.file))
      await api.post(`/exams/${createdExamId}/submissions`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div style={S.page}>
      <h2 style={S.h2}>{isNew ? 'Create Exam & Upload Submissions' : 'Upload Submissions'}</h2>

      {isNew && !createdExamId && (
        <form onSubmit={handleCreateExam} style={S.section}>
          <p style={S.sectionLabel}>Exam Details</p>
          <input style={S.input} placeholder="Exam Title" value={examForm.title} required
            onChange={(e) => setExamForm({ ...examForm, title: e.target.value })} />
          <input style={S.input} placeholder="Course Code (e.g. CS101)" value={examForm.course_code} required
            onChange={(e) => setExamForm({ ...examForm, course_code: e.target.value })} />
          <textarea style={{ ...S.input, minHeight: 160, fontFamily: 'monospace', fontSize: 12 }}
            placeholder={'{\n  "questions": [\n    { "number": 1, "text": "...", "max_score": 10, "criteria": [...] }\n  ]\n}'}
            value={examForm.rubric} required
            onChange={(e) => setExamForm({ ...examForm, rubric: e.target.value })} />
          {error && <p style={S.err}>{error}</p>}
          <button type="submit" style={S.btn}>Create Exam →</button>
        </form>
      )}

      {createdExamId && (
        <form onSubmit={handleUpload} style={S.section}>
          <p style={S.sectionLabel}>Student Submissions</p>
          {rows.map((row, i) => (
            <div key={i} style={S.row}>
              <input style={{ ...S.input, flex: 1 }} placeholder="Student Name"
                value={row.name} onChange={(e) => updateRow(i, 'name', e.target.value)} required />
              <input style={{ ...S.input, flex: 1 }} placeholder="Student ID"
                value={row.studentId} onChange={(e) => updateRow(i, 'studentId', e.target.value)} required />
              <input type="file" accept="application/pdf" required style={{ color: '#aaa', flex: 1 }}
                onChange={(e) => updateRow(i, 'file', e.target.files[0])} />
            </div>
          ))}
          <button type="button" onClick={() => setRows([...rows, { name: '', studentId: '', file: null }])}
            style={{ ...S.btn, background: '#16213e', marginBottom: 8 }}>
            + Add Row
          </button>
          {error && <p style={S.err}>{error}</p>}
          <button type="submit" style={S.btn} disabled={uploading}>
            {uploading ? 'Uploading & Queuing…' : 'Upload & Start Grading'}
          </button>
        </form>
      )}
    </div>
  )
}

const S = {
  page: { maxWidth: 800, margin: '40px auto', padding: '0 24px' },
  h2: { color: '#fff', marginBottom: 24 },
  section: { background: '#1a1a2e', padding: 24, borderRadius: 10, display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 24 },
  sectionLabel: { color: '#e94560', fontWeight: 600, fontSize: 13, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4 },
  input: { padding: '9px 13px', borderRadius: 6, border: '1px solid #2a2a3e', background: '#0f0f1a', color: '#fff', fontSize: 14, width: '100%', outline: 'none' },
  row: { display: 'flex', gap: 10, alignItems: 'center' },
  btn: { padding: 10, borderRadius: 6, background: '#e94560', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: 14 },
  err: { color: '#e94560', fontSize: 13 },
}
