import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import SymptomChecker from './pages/SymptomChecker'
import AnalysisResults from './pages/AnalysisResults'
import History from './pages/History'
import Profile from './pages/Profile' // Stub for now
import MedicalHistory from './pages/MedicalHistory'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="checker" element={<SymptomChecker />} />
        <Route path="results" element={<AnalysisResults />} />
        <Route path="history" element={<History />} />
        <Route path="profile" element={<Profile />} />
        <Route path="history/medical" element={<MedicalHistory />} />
      </Route>
    </Routes>
  )
}

export default App
