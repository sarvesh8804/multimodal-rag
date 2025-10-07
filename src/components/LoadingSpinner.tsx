import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
}

export function LoadingSpinner({ message = 'Loading...' }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-4">
      <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
      <p className="text-gray-400 text-sm">{message}</p>
    </div>
  );
}

export function FullScreenLoader({ message = 'Loading...' }: LoadingSpinnerProps) {
  return (
    <div className="fixed inset-0 bg-gray-900/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-2xl p-8 shadow-2xl flex flex-col items-center gap-4">
        <Loader2 className="w-16 h-16 text-blue-500 animate-spin" />
        <p className="text-white text-lg font-medium">{message}</p>
      </div>
    </div>
  );
}
