import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingState = ({ message = 'Loading details...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <Loader2 className="w-10 h-10 animate-spin text-blue-600 mb-4" />
      <p className="text-slate-600 font-medium">{message}</p>
    </div>
  );
};

export default LoadingState;
