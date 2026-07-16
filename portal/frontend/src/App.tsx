import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HubLanding from './pages/HubLanding'
import { ThemeProvider } from './lib/ThemeContext'
import './App.css'

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/" element={<HubLanding />} />
          <Route path="/agents" element={<div>Agent Registry (Coming soon)</div>} />
          <Route path="/tools" element={<div>Tool Explorer (Coming soon)</div>} />
          <Route path="/knowledge" element={<div>Knowledge Base (Coming soon)</div>} />
          <Route path="/docs" element={<div>Documentation (Coming soon)</div>} />
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App
