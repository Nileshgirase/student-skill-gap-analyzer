import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Compass, PlusCircle, LogOut, User as UserIcon } from 'lucide-react';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center gap-8">
            <Link to={isAuthenticated ? '/dashboard' : '/'} className="flex items-center gap-2.5 font-bold text-lg text-slate-900">
              <div className="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center text-white shadow-sm shadow-blue-200">
                <Compass className="w-5 h-5" />
              </div>
              <span className="hidden sm:inline">SkillGap Analyzer</span>
            </Link>

            {isAuthenticated && (
              <div className="hidden md:flex items-center gap-1">
                <Link
                  to="/dashboard"
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition ${
                    isActive('/dashboard') ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/new-analysis"
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition ${
                    isActive('/new-analysis') ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  New Analysis
                </Link>
              </div>
            )}
          </div>

          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <>
                <Link
                  to="/new-analysis"
                  className="hidden sm:inline-flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-3.5 py-1.5 rounded-lg shadow-sm transition"
                >
                  <PlusCircle className="w-4 h-4" />
                  <span>Start Analysis</span>
                </Link>
                <div className="flex items-center gap-2 pl-2 border-l border-slate-200 text-slate-700 text-sm">
                  <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-600">
                    <UserIcon className="w-4 h-4" />
                  </div>
                  <span className="hidden lg:inline font-medium text-slate-800">{user?.name}</span>
                </div>
                <button
                  onClick={handleLogout}
                  title="Sign out"
                  className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="text-slate-700 hover:text-slate-900 px-3.5 py-1.5 text-sm font-medium rounded-lg hover:bg-slate-50 transition"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-3.5 py-1.5 rounded-lg shadow-sm transition"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
