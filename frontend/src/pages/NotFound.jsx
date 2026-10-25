import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, Home } from 'lucide-react';

const NotFound = () => {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <div className="bg-white border border-slate-200 rounded-2xl p-10 max-w-md text-center shadow-sm">
        <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Compass className="w-8 h-8" />
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900">404</h1>
        <h2 className="text-lg font-bold text-slate-800 mt-1">Page Not Found</h2>
        <p className="text-sm text-slate-600 mt-2">
          The page or analysis you requested could not be located.
        </p>
        <Link
          to="/dashboard"
          className="mt-6 inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-5 py-2.5 rounded-xl shadow-md shadow-blue-200 transition"
        >
          <Home className="w-4 h-4" />
          <span>Return to Dashboard</span>
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
