import { Loader2, Sparkles } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
}

export function LoadingSpinner({ message = 'Loading...' }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-6 animate-fade-in-up">
      <div className="relative">
        <div className="absolute inset-0 bg-primary/30 dark:bg-primary/20 rounded-full blur-3xl animate-pulse-glow" />
        <div className="relative w-16 h-16 rounded-3xl glass-card flex items-center justify-center shadow-2xl border border-primary/20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      </div>
      <p className="text-muted-foreground text-base font-semibold tracking-tight">{message}</p>
    </div>
  );
}

export function FullScreenLoader({ message = 'Loading...' }: LoadingSpinnerProps) {
  return (
    <div className="fixed inset-0 bg-background/98 backdrop-blur-2xl flex items-center justify-center z-50 animate-fade-in">
      <div className="glass-card rounded-[3rem] p-16 shadow-2xl flex flex-col items-center gap-10 max-w-md mx-4 border border-border/50 animate-fade-in-up">
        <div className="relative">
          <div className="absolute inset-0 bg-primary/30 dark:bg-primary/20 rounded-full blur-3xl animate-pulse-glow" />
          <div className="relative w-28 h-28 rounded-[2.5rem] glass-card flex items-center justify-center shadow-2xl border-2 border-primary/20">
            <div className="w-20 h-20 rounded-[2rem] bg-gradient-to-br from-primary to-accent flex items-center justify-center">
              <Sparkles className="w-10 h-10 text-white animate-pulse" />
            </div>
          </div>
        </div>
        <div className="text-center space-y-3">
          <p className="font-display text-3xl font-bold gradient-text text-glow tracking-tight">{message}</p>
          <p className="text-base text-muted-foreground font-medium">Please wait a moment</p>
        </div>
      </div>
    </div>
  );
}
