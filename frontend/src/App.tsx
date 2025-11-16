import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'

// Pages
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import MarketplacePage from './pages/MarketplacePage'
import MyModulesPage from './pages/MyModulesPage'
import ProfilePage from './pages/ProfilePage'

// CV Analysis Pages
import CVUploadPage from './pages/cv-analysis/CVUploadPage'
import CVListPage from './pages/cv-analysis/CVListPage'
import CVDetailPage from './pages/cv-analysis/CVDetailPage'
import ATSCheckerPage from './pages/cv-analysis/ATSCheckerPage'
import RealJobMatcherPage from '@/pages/cv-analysis/RealJobMatcherPage'
import AdvancedAnalyzerPage from './pages/cv-analysis/AdvancedAnalyzerPage'

// Interview Pages
import InterviewListPage from './pages/interviews/InterviewListPage'
import InterviewSessionPage from './pages/interviews/InterviewSessionPage'
import InterviewResultsPage from './pages/interviews/InterviewResultsPage'
import InterviewSimulatorPage from './pages/InterviewSimulatorPage'

// Code Assessment Pages
import CodeProblemsPage from './pages/code-assessment/CodeProblemsPage'

// Layouts
import AuthLayout from './components/layouts/AuthLayout'
import DashboardLayout from './components/layouts/DashboardLayout'

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

function App() {
  return (
    <Router>
      <Routes>
        {/* Auth Routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>

        {/* Protected Dashboard Routes */}
        <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/marketplace" element={<MarketplacePage />} />
          <Route path="/my-modules" element={<MyModulesPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          
          {/* CV Analysis Routes */}
          <Route path="/cv-analysis/upload" element={<CVUploadPage />} />
          <Route path="/cv-analysis/cvs" element={<CVListPage />} />
          <Route path="/cv-analysis/cvs/:id" element={<CVDetailPage />} />
          
          {/* New CV Analysis Module Routes */}
          <Route path="/cv-analysis/ats-checker" element={<ATSCheckerPage />} />
              <Route path="/cv-analysis/cv-job-matcher" element={<RealJobMatcherPage />} />
          <Route path="/cv-analysis/advanced-analyzer" element={<AdvancedAnalyzerPage />} />
          
          {/* Interview Routes */}
          <Route path="/interviews" element={<InterviewListPage />} />
          <Route path="/interviews/:id" element={<InterviewSessionPage />} />
          <Route path="/interviews/:id/results" element={<InterviewResultsPage />} />
          <Route path="/interview-simulator" element={<InterviewSimulatorPage />} />
          
          {/* Code Assessment Routes */}
          <Route path="/code-assessment" element={<CodeProblemsPage />} />
        </Route>

        {/* Default Route */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  )
}

export default App
