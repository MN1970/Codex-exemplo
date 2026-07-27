import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { FullBleedLayout } from '@/components/layout/FullBleedLayout'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { Home } from '@/pages/Home'
import { Login } from '@/pages/Login'
import { Register } from '@/pages/Register'
import { Canvas } from '@/pages/Canvas'
import { KnowledgeHub } from '@/pages/KnowledgeHub'
import { NotFound } from '@/pages/NotFound'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
          <Route element={<ProtectedRoute />}>
            <Route index element={<Home />} />
            <Route path="knowledge-hub" element={<KnowledgeHub />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Route>
        {/* Full-bleed shell (no max-w/padding) for app-like pages. */}
        <Route element={<FullBleedLayout />}>
          <Route element={<ProtectedRoute />}>
            <Route path="canvas" element={<Canvas />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
