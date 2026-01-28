import { useEffect } from 'react';
import { CheckCircle, XCircle, Info, X, AlertCircle } from 'lucide-react';

interface Toast {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}

interface ToastProps {
  toast: Toast;
  onClose: (id: string) => void;
}

export function ToastNotification({ toast, onClose }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose(toast.id);
    }, 5000);

    return () => clearTimeout(timer);
  }, [toast.id, onClose]);

  const icons = {
    success: <CheckCircle className="w-5 h-5" />,
    error: <XCircle className="w-5 h-5" />,
    info: <Info className="w-5 h-5" />,
    warning: <AlertCircle className="w-5 h-5" />,
  };

  const styles = {
    success: 'glass-card border-primary/50 text-foreground',
    error: 'glass-card border-destructive/50 text-foreground',
    info: 'glass-card border-accent/50 text-foreground',
    warning: 'glass-card border-secondary/50 text-foreground',
  };

  const iconColors = {
    success: 'text-primary',
    error: 'text-destructive',
    info: 'text-accent',
    warning: 'text-secondary',
  };

  return (
    <div
      className={`${styles[toast.type]} px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-4 min-w-[340px] max-w-md animate-slide-up hover-lift`}
    >
      <div className={`${iconColors[toast.type]} flex-shrink-0`}>{icons[toast.type]}</div>
      <p className="flex-1 text-sm font-medium leading-relaxed">{toast.message}</p>
      <button
        onClick={() => onClose(toast.id)}
        className="hover:bg-muted/50 rounded-lg p-2 transition-colors text-muted-foreground hover:text-foreground flex-shrink-0"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}

interface ToastContainerProps {
  toasts: Toast[];
  onClose: (id: string) => void;
}

export function ToastContainer({ toasts, onClose }: ToastContainerProps) {
  return (
    <div className="fixed top-8 right-8 z-50 flex flex-col gap-4">
      {toasts.map((toast) => (
        <ToastNotification key={toast.id} toast={toast} onClose={onClose} />
      ))}
    </div>
  );
}
