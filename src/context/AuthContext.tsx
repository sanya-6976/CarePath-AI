import React, { createContext, useContext, useState, useEffect } from 'react';
import type { UserProfile } from '../types';
import { authService } from '../services/authService';

interface AuthContextType {
  user: UserProfile | null;
  patientId: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user: UserProfile, patientId?: string) => void;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [patientId, setPatientId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const login = (token: string, userProfile: UserProfile, pId?: string) => {
    localStorage.setItem('carepath_token', token);
    setUser(userProfile);
    if (pId) {
      localStorage.setItem('carepath_patient_id', pId);
      setPatientId(pId);
    } else {
      const storedPid = localStorage.getItem('carepath_patient_id') || 'demo_patient_id';
      setPatientId(storedPid);
    }
  };

  const logout = () => {
    localStorage.removeItem('carepath_token');
    localStorage.removeItem('carepath_patient_id');
    setUser(null);
    setPatientId(null);
  };

  const refreshProfile = async () => {
    try {
      const profile = await authService.getProfile();
      setUser(profile);
    } catch (err) {
      console.error('Failed to refresh user profile:', err);
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('carepath_token');
      const storedPid = localStorage.getItem('carepath_patient_id');
      
      if (token) {
        setPatientId(storedPid || 'demo_patient_id');
        try {
          if (token === 'demo_token') {
            setUser({
              id: 'demo_user',
              email: 'demo@carepath.ai',
              name: 'Demo Patient',
            });
          } else {
            const profile = await authService.getProfile();
            setUser(profile);
            setPatientId(storedPid || profile.id || null);
          }
        } catch (err) {
          console.error('Session validation failed:', err);
          logout();
        }
      }
      setIsLoading(false);
    };

    initAuth();

    const handleAuthExpired = () => {
      logout();
    };

    window.addEventListener('auth_expired', handleAuthExpired);
    return () => {
      window.removeEventListener('auth_expired', handleAuthExpired);
    };
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        patientId,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
