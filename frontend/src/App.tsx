import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Layouts
import LandingLayout from './layouts/LandingLayout';
import AuthLayout from './layouts/AuthLayout';
import DashboardLayout from './layouts/DashboardLayout';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DashBoardingPage from './pages/DashBoardingPage';
import ProfilePage from './pages/ProfilePage';
import UploadCenterPage from './pages/UploadCenterPage';
import AIInvestigationPage from './pages/AIInvestigationPage';
import RecommendationPage from './pages/RecommendationPage';
import CareJourneyPage from './pages/CareJourneyPage';
import TimelinePage from './pages/TimelinePage';
import MedicalRecordsPage from './pages/MedicalRecordsPage';
import FollowUpPage from './pages/FollowUpPage';
import NotificationsPage from './pages/NotificationsPage';
import NotFoundPage from './pages/NotFoundPage';
import SettingsPage from './pages/SettingsPage';
import MedicationsPage from './pages/MedicationsPage';
import DoctorBridgePage from './pages/DoctorBridgePage';

// Protected Route Guard
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  // Dev-only auth bypass
  const isBypassEnabled = !import.meta.env.PROD && import.meta.env.VITE_DEV_BYPASS_AUTH === 'true';
  if (isBypassEnabled) {
    return <>{children}</>;
  }
  
  if (isLoading) {
    return (
      <div className="min-h-screen bg-brand-bg flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-lavender"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Landing Page Route */}
        <Route element={<LandingLayout />}>
          <Route path="/" element={<LandingPage />} />
        </Route>

        {/* Authentication Routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
        </Route>

        {/* Dashboard Routes (Protected) */}
        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<DashBoardingPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/upload" element={<UploadCenterPage />} />
          <Route path="/analysis/processing" element={<AIInvestigationPage />} />
          <Route path="/analysis" element={<RecommendationPage />} />
          <Route path="/journey" element={<CareJourneyPage />} />
          <Route path="/timeline" element={<TimelinePage />} />
          {/* Medical Records */}
          <Route path="/records" element={<MedicalRecordsPage />} />
          {/* Medications */}
          <Route path="/medications" element={<MedicationsPage />} />
          {/* Doctor Bridge */}
          <Route path="/doctor-bridge" element={<DoctorBridgePage />} />
          {/* Follow-up */}
          <Route path="/followup" element={<FollowUpPage />} />
          <Route path="/follow-up" element={<FollowUpPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>

        {/* 404 Route */}
        <Route path="/404" element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
