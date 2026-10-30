import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Compass, Mail, Lock, ArrowRight, AlertCircle, Info } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [slowServerNotice, setSlowServerNotice] = useState(false);

  const isExpired = new URLSearchParams(location.search).get('expired') === 'true';
  const isResetSuccess = new URLSearchParams(location.search).get('reset') === 'success';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSlowServerNotice(false);
    setSubmitting(true);

    const timer = setTimeout(() => {
      setSlowServerNotice(true);
    }, 4000);

    try {
      await login(email, password);
      clearTimeout(timer);
      const origin = location.state?.from?.pathname || '/dashboard';
      navigate(origin, { replace: true });
    } catch (err) {
      clearTimeout(timer);
      if (err.response) {
        if (err.response.status === 401) {
          setError(err.response.data?.detail || 'Invalid email or password. Please verify your credentials.');
        } else if (err.response.status === 422) {
          setError('Please provide a valid email address and password.');
        } else if (err.response.status >= 500) {
          setError('The server encountered a temporary error or is restarting. Please try again shortly.');
        } else {
          setError(err.response.data?.detail || 'Authentication failed. Please try again.');
        }
      } else if (err.code === 'ECONNABORTED') {
        setError('Connection timed out. The server may be waking up from an idle state. Please wait a few moments and try again.');
      } else {
        setError('Network error: Unable to reach the server. Please check your internet connection or try again in a moment.');
      }
    } finally {
      clearTimeout(timer);
      setSubmitting(false);
      setSlowServerNotice(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white border border-slate-200 rounded-2xl shadow-xl shadow-slate-200/50 p-8">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-600 rounded-xl text-white shadow-md shadow-blue-200 mb-3">
            <Compass className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900">Student Sign In</h1>
          <p className="text-sm text-slate-600 mt-1">
            Access your verified job gap analyses and learning roadmaps.
          </p>
        </div>

        {isResetSuccess && (
          <div className="mb-4 p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl flex items-start gap-2.5 text-xs text-emerald-800">
            <Info className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <span>Your password has been successfully reset. Please sign in with your new password.</span>
          </div>
        )}

        {isExpired && (
          <div className="mb-4 p-3.5 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-2.5 text-xs text-amber-800">
            <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <span>Your session has expired. Please sign in again to continue.</span>
          </div>
        )}

        {error && (
          <div className="mb-5 p-3.5 bg-rose-50 border border-rose-200 rounded-xl flex items-start gap-2.5 text-xs text-rose-700">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {slowServerNotice && submitting && (
          <div className="mb-5 p-3.5 bg-blue-50 border border-blue-200 rounded-xl flex items-start gap-2.5 text-xs text-blue-800 animate-pulse">
            <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
            <span>Connecting to backend service... If this is your first request after inactivity, the server is waking up. Please hold on.</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="student@university.edu"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition"
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-semibold text-slate-700">Password</label>
              <Link to="/forgot-password" className="text-xs font-medium text-blue-600 hover:underline">
                Forgot password?
              </Link>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full mt-2 py-3 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-xl shadow-md shadow-blue-200 transition flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <span>{submitting ? 'Authenticating...' : 'Sign In'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-6 pt-5 border-t border-slate-100 text-center text-xs text-slate-600">
          New to the analyzer?{' '}
          <Link to="/register" className="font-semibold text-blue-600 hover:underline">
            Create an account
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
