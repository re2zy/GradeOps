import { configureStore, createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../api'

// ── Auth ─────────────────────────────────────────────────────────────────────

export const login = createAsyncThunk('auth/login', async (credentials, { rejectWithValue }) => {
  try {
    const { data: tokenData } = await api.post('/auth/login', credentials)
    api.defaults.headers.common['Authorization'] = `Bearer ${tokenData.access_token}`
    const { data: user } = await api.get('/auth/me')
    localStorage.setItem('token', tokenData.access_token)
    localStorage.setItem('user', JSON.stringify(user))
    return { token: tokenData.access_token, user }
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Login failed')
  }
})

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null,
  },
  reducers: {
    logout(state) {
      state.user = null
      state.token = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete api.defaults.headers.common['Authorization']
    },
  },
  extraReducers: (b) => {
    b.addCase(login.pending, (s) => { s.loading = true; s.error = null })
    b.addCase(login.fulfilled, (s, a) => { s.loading = false; s.token = a.payload.token; s.user = a.payload.user })
    b.addCase(login.rejected, (s, a) => { s.loading = false; s.error = a.payload })
  },
})

export const { logout } = authSlice.actions

// ── Exams ─────────────────────────────────────────────────────────────────────

export const fetchExams = createAsyncThunk('exams/fetchAll', async (_, { rejectWithValue }) => {
  try {
    const { data } = await api.get('/exams/')
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Failed to load exams')
  }
})

const examsSlice = createSlice({
  name: 'exams',
  initialState: { list: [], loading: false, error: null },
  reducers: {},
  extraReducers: (b) => {
    b.addCase(fetchExams.pending, (s) => { s.loading = true })
    b.addCase(fetchExams.fulfilled, (s, a) => { s.loading = false; s.list = a.payload })
    b.addCase(fetchExams.rejected, (s, a) => { s.loading = false; s.error = a.payload })
  },
})

// ── Grades / Review ───────────────────────────────────────────────────────────

export const fetchPendingGrades = createAsyncThunk('grades/fetchPending', async (examId, { rejectWithValue }) => {
  try {
    const { data } = await api.get(`/review/pending?exam_id=${examId}`)
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail)
  }
})

export const fetchReviewStats = createAsyncThunk('grades/fetchStats', async (examId) => {
  const { data } = await api.get(`/review/stats/${examId}`)
  return data
})

export const submitReview = createAsyncThunk(
  'grades/submitReview',
  async ({ gradeId, action, score, comment }, { rejectWithValue }) => {
    try {
      await api.post(`/review/${gradeId}`, { action, ta_override_score: score, ta_comment: comment })
      return gradeId
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail)
    }
  },
)

const gradesSlice = createSlice({
  name: 'grades',
  initialState: { pendingGrades: [], currentIndex: 0, stats: null, loading: false, error: null },
  reducers: {
    nextGrade(s) { if (s.currentIndex < s.pendingGrades.length - 1) s.currentIndex++ },
    prevGrade(s) { if (s.currentIndex > 0) s.currentIndex-- },
    removeReviewed(s, a) {
      s.pendingGrades = s.pendingGrades.filter((g) => g.id !== a.payload)
      if (s.currentIndex >= s.pendingGrades.length) s.currentIndex = Math.max(0, s.pendingGrades.length - 1)
    },
  },
  extraReducers: (b) => {
    b.addCase(fetchPendingGrades.pending, (s) => { s.loading = true })
    b.addCase(fetchPendingGrades.fulfilled, (s, a) => { s.loading = false; s.pendingGrades = a.payload; s.currentIndex = 0 })
    b.addCase(fetchReviewStats.fulfilled, (s, a) => { s.stats = a.payload })
    b.addCase(submitReview.fulfilled, (s, a) => { s.pendingGrades = s.pendingGrades.filter((g) => g.id !== a.payload) })
  },
})

export const { nextGrade, prevGrade, removeReviewed } = gradesSlice.actions

// ── Store ─────────────────────────────────────────────────────────────────────

export default configureStore({
  reducer: {
    auth: authSlice.reducer,
    exams: examsSlice.reducer,
    grades: gradesSlice.reducer,
  },
})
