import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Lock, Mail, AlertTriangle, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/authService';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login: authLogin } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const demoAccessEnabled = !import.meta.env.PROD && import.meta.env.VITE_DEV_BYPASS_AUTH === 'true';

  const continueWithDemo = () => {
    authLogin('demo_token', {
      id: 'demo_user',
      email: 'demo@carepath.ai',
      name: 'Demo Patient',
      role: 'patient',
    }, 'demo_patient_id');
    navigate('/dashboard');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      const data: any = await authService.login({ email, password });
      
      const token = data.token || data.access_token || 'mock_jwt_token';
      const userProfile = data.user || {
        id: data.user_id || 'demo_user',
        email: email,
        name: email.split('@')[0],
        role: 'patient',
      };
      const pId = data.patient_id || data.patient?.id || userProfile.id;

      // Update AuthContext state
      authLogin(token, userProfile, pId);

      navigate('/dashboard');
    } catch (err: any) {
      console.error('Login error:', err);
      setError(
        err.message === 'Failed to fetch'
          ? 'Cannot connect to backend server. Ensure the API service is running at https://carepath-ai-production-508e.up.railway.app.'
          : err.message || 'Login failed. Please verify your email and password.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div className="text-center mb-6">
        <h2 className="font-display text-2xl font-bold text-brand-plum mb-2">Welcome Back</h2>
        <p className="text-brand-slate text-sm">Sign in to resume your active care path.</p>
      </div>

      {error && (
        <div className="bg-brand-rose-bg border border-brand-rose-text/10 text-brand-rose-text p-3 rounded-xl text-xs flex items-start gap-2.5 mb-5">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {/* Email Field */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-brand-slate px-1">Email Address</label>
          <div className="relative">
            <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-brand-slate" />
            <input
              type="email"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl pl-10 pr-4 py-3 text-sm focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none transition-all"
              required
            />
          </div>
        </div>

        {/* Password Field */}
        <div className="flex flex-col gap-1.5">
          <div className="flex justify-between items-center px-1">
            <label className="text-xs font-semibold text-brand-slate">Password</label>
          </div>
          <div className="relative">
            <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-brand-slate" />
            <input
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl pl-10 pr-10 py-3 text-sm focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none transition-all"
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-brand-slate hover:text-brand-plum rounded-lg"
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="bg-brand-lavender hover:bg-brand-lavender-hover disabled:bg-brand-lavender/50 text-white font-semibold text-sm py-3 rounded-xl transition-all shadow-sm flex items-center justify-center gap-2 mt-2 cursor-pointer"
        >
          {isLoading ? 'Signing In...' : 'Sign In'}
          {!isLoading && <ArrowRight className="w-4 h-4" />}
        </button>
      </form>

      {/* Alternative actions */}
      <div className="mt-6 flex flex-col gap-3 text-center border-t border-brand-slate/10 pt-5">
        <span className="text-xs text-brand-slate">
          Don't have an account?{' '}
          <Link to="/signup" className="text-brand-lavender hover:underline font-semibold">
            Create account
          </Link>
        </span>
        {demoAccessEnabled && (
          <button
            type="button"
            onClick={continueWithDemo}
            className="text-xs text-brand-slate hover:text-brand-lavender font-semibold underline underline-offset-4"
          >
            Continue with local demo access
          </button>
        )}
      </div>
    </div>
  );
}
