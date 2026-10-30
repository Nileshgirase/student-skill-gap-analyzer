import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { forgotPassword } from '../api/auth';
import { Compass, Mail, ArrowRight, ArrowLeft, AlertCircle, CheckCircle2, Info } from 'lucide-react';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [successInfo, setSuccessInfo] = useState(null);
  const [slowServerNotice, setSlowServerNotice] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSlowServerNotice(false);
    setSubmitting(true);

    const timer = setTimeout(() => {
      setSlowServerNotice(true);
    }, 4000);

    try {
      const response = await forgotPassword({ email });
      clearTimeout(timer);
      setSuccessInfo(response);
    } catch (err) {
      clearTimeout(timer);
      if (err.response?.status === 422) {
        setError('Please enter a valid email address.');
      } else {
        setError(err.response?.data?.detail || 'Unable to process reset request. Please try again.');
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
          <h1 className="text-2xl font-extrabold text-slate-900">Reset Password</h1>
          <p className="text-sm text-slate-600 mt-1">
            Enter your registered email to receive secure password reset instructions.
          </p>
        </div>

        {error && (
          <div className="mb-5 p-3.5 bg-rose-50 border border-rose-200 rounded-xl flex items-start gap-2.5 text-xs text-rose-700">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {slowServerNotice && submitting && (
          <div className="mb-5 p-3.5 bg-blue-50 border border-blue-200 rounded-xl flex items-start gap-2.5 text-xs text-blue-800 animate-pulse">
            <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
            <span>Contacting server... If waking from an idle state, this may take a moment.</span>
          </div>
        )}

        {successInfo ? (
          <div className="space-y-5">
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-start gap-3 text-xs text-emerald-800">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-emerald-900 mb-1">Check Your Inbox</p>
                <p className="leading-relaxed">{successInfo.message}</p>
              </div>
            </div>

            {/* Development / Testing Quick Link */}
            {successInfo.reset_token && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-900">
                <p className="font-bold mb-1 flex items-center gap-1.5">
                  <Info className="w-4 h-4 text-blue-600" />
                  <span>Local Development Mode</span>
                </p>
                <p className="text-slate-600 mb-3">
                  SMTP is not configured in this environment. You can directly proceed using the generated test token:
                </p>
                <Link
                  to={`/reset-password?token=${successInfo.reset_token}`}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-sm transition"
                >
                  <span>Open Password Reset Page</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            )}

            <div className="pt-2 text-center">
              <Link
                to="/login"
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 transition"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Return to Sign In</span>
              </Link>
            </div>
          </div>
        ) : (
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

            <button
              type="submit"
              disabled={submitting}
              className="w-full mt-2 py-3 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-xl shadow-md shadow-blue-200 transition flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <span>{submitting ? 'Sending Request...' : 'Send Reset Instructions'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <div className="pt-3 text-center">
              <Link
                to="/login"
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 transition"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Back to Sign In</span>
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default ForgotPassword;
