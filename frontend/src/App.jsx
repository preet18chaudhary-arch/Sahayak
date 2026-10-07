import { useEffect, useState } from 'react'
import './App.css'

import { Navbar } from './components/Navbar'
import { LoginPage } from './components/LoginPage'
import { LandingPage } from './components/LandingPage'
import { VerificationDashboard } from './components/VerificationDashboard'

import {
  createSession,
  getScholarships,
  getSession,
  resolveDiscrepancy,
  uploadSingleDocument,
} from './services/api'

function App() {
  // Login state
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [loggedInUser, setLoggedInUser] = useState('')

  // Application state
  const [screen, setScreen] = useState('home')
  const [studentName, setStudentName] = useState('Hana Sharma')
  const [scholarships, setScholarships] = useState([])
  const [selectedScholarshipId, setSelectedScholarshipId] =
    useState('merit-cum-means')
  const [session, setSession] = useState(null)

  // Loading & error states
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Upload states
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState({
    current: 0,
    total: 0,
    currentFileName: '',
  })
  const [lastUploadResult, setLastUploadResult] = useState(null)
  const [uploadError, setUploadError] = useState('')

  // Discrepancy resolution state
  const [resolvingId, setResolvingId] = useState(null)

  // Login
  function handleLogin(name) {
    setLoggedInUser(name)
    setStudentName(name)
    setIsLoggedIn(true)
  }

  // Logout
  function handleLogout() {
    setIsLoggedIn(false)
    setLoggedInUser('')
    setSession(null)
    setScreen('home')
    setError('')
    setUploadError('')
    setLastUploadResult(null)
  }

  // Load available scholarship rule presets on mount
  useEffect(() => {
    async function initScholarships() {
      try {
        const schemes = await getScholarships()
        setScholarships(schemes)

        if (schemes.length > 0) {
          setSelectedScholarshipId(schemes[0].scholarship_id)
        }
      } catch {
        // Fallback demo preset if backend not yet reached
        setScholarships([
          {
            scholarship_id: 'merit-cum-means',
            name: 'National Merit-cum-Means Scholarship',
            description:
              'Merit scholarship for students with family income <= ₹2.5 LPA and marks >= 60%.',
            required_documents: [
              'aadhaar',
              'marksheet_12th',
              'income_certificate',
            ],
            income_ceiling: 250000.0,
            min_academic_percentage: 60.0,
            matching_thresholds: {
              auto_approve_threshold: 0.98,
              human_review_threshold: 0.8,
            },
          },
        ])
      }
    }

    initScholarships()
  }, [])

  // Start Verification flow
  async function handleStartVerification() {
    if (!studentName.trim()) {
      setError('Please enter your full name to proceed.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const newSession = await createSession(
        studentName.trim(),
        selectedScholarshipId
      )

      setSession(newSession)
      setScreen('dashboard')
    } catch {
      setError(
        'Could not connect to Sahayak backend. Please ensure the FastAPI server is running on http://127.0.0.1:8001.'
      )
    } finally {
      setLoading(false)
    }
  }

  // Upload multiple documents sequentially to the real backend upload endpoint
  async function handleUploadFiles(files) {
    if (!session || files.length === 0) return false

    setUploading(true)
    setUploadError('')
    setLastUploadResult(null)

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i]

        setUploadProgress({
          current: i + 1,
          total: files.length,
          currentFileName: file.name,
        })

        // Call real backend upload endpoint
        const uploadResult = await uploadSingleDocument(
          session.session_id,
          file
        )

        setLastUploadResult(uploadResult)

        // Refresh session using the real GET session endpoint
        const refreshedSession = await getSession(session.session_id)
        setSession(refreshedSession)
      }

      return true
    } catch (err) {
      setUploadError(
        err.message || 'An error occurred during document upload.'
      )

      // Refresh session anyway to display whatever succeeded
      try {
        const refreshed = await getSession(session.session_id)
        setSession(refreshed)
      } catch {
        // Ignore refresh error
      }

      return false
    } finally {
      setUploading(false)
    }
  }

  // Resolve a discrepancy and refresh session
  async function handleResolveDiscrepancy(
    discrepancyId,
    resolutionNote
  ) {
    if (!session) return false

    setResolvingId(discrepancyId)
    setUploadError('')

    try {
      await resolveDiscrepancy(
        session.session_id,
        discrepancyId,
        resolutionNote
      )

      // Refresh session from real GET endpoint
      const refreshedSession = await getSession(session.session_id)
      setSession(refreshedSession)

      return true
    } catch (err) {
      setUploadError(
        err.message || 'Failed to resolve discrepancy.'
      )

      return false
    } finally {
      setResolvingId(null)
    }
  }

  // Start a new verification session
  function handleReset() {
    setScreen('home')
    setSession(null)
    setError('')
    setUploadError('')
    setLastUploadResult(null)
  }

  // Show login page before the main application
  if (!isLoggedIn) {
    return (
      <div className="app">
        <Navbar />
        <LoginPage onLogin={handleLogin} />
      </div>
    )
  }

  return (
    <div className="app">
      <Navbar
        onReset={session ? handleReset : null}
        session={session}
        loggedInUser={loggedInUser}
        onLogout={handleLogout}
      />

      {screen === 'home' ? (
        <LandingPage
          studentName={studentName}
          setStudentName={setStudentName}
          scholarships={scholarships}
          selectedScholarshipId={selectedScholarshipId}
          setSelectedScholarshipId={setSelectedScholarshipId}
          onStartVerification={handleStartVerification}
          loading={loading}
          error={error}
        />
      ) : (
        <VerificationDashboard
          session={session}
          onUploadFiles={handleUploadFiles}
          uploading={uploading}
          uploadProgress={uploadProgress}
          lastUploadResult={lastUploadResult}
          uploadError={uploadError}
          onResolveDiscrepancy={handleResolveDiscrepancy}
          resolvingId={resolvingId}
          onNewSession={handleReset}
        />
      )}
    </div>
  )
}

export default App