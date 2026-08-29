import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { AuthProvider } from './context/AuthContext'
import { PatientProvider } from './context/PatientContext'
import { PreferencesProvider } from './context/PreferencesContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <PatientProvider>
        <PreferencesProvider>
          <App />
        </PreferencesProvider>
      </PatientProvider>
    </AuthProvider>
  </StrictMode>,
)
