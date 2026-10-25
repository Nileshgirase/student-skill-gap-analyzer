import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';

const ErrorState = ({ title = 'An error occurred', message, onRetry }) => {
  return (
    <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 my-4 text-left">
      <div className="flex items-start gap-3">
        <AlertCircle className="w-6 h-6 text-rose-600 shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="text-base font-semibold text-rose-900">{title}</h3>
          {message && <p className="text-sm text-rose-700 mt-1">{message}</p>}
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-rose-600 hover:bg-rose-700 text-white rounded-lg transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorState;
