import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <header>
          <h1>Portal Knowledge | Manta Maestro v5.0</h1>
          <p>ADK-5 Layer Architecture — Agent Registry & Knowledge Base</p>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<div>Dashboard (Coming soon)</div>} />
            <Route path="/agents" element={<div>Agent Registry (Coming soon)</div>} />
            <Route path="/tools" element={<div>Tool Explorer (Coming soon)</div>} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
