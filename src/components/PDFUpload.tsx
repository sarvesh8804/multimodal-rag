import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle, Loader2, Sparkles } from 'lucide-react';
import { Button } from '../components/ui/button';
import { ThemeToggle } from '../components/ThemeToggle';

interface PDFUploadProps {
  onUploadSuccess: (docId: string, filename: string) => void;
  onUploadError: (error: string) => void;
  isUploading: boolean;
  setIsUploading: (loading: boolean) => void;
}

export function PDFUpload({
  onUploadSuccess,
  onUploadError,
  isUploading,
  setIsUploading,
}: PDFUploadProps) {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    setError(null);
    setUploadProgress(0);

    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => (prev >= 90 ? 90 : prev + 10));
    }, 200);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/upload_pdf', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Upload failed' }));
        throw new Error(errorData.error || 'Failed to upload document');
      }

      const data = await response.json();
      setUploadProgress(100);

      setTimeout(() => {
        onUploadSuccess(data.doc_id, file.name);
      }, 500);
    } catch (error) {
      clearInterval(progressInterval);
      setUploadProgress(0);
      const errorMessage = error instanceof Error 
        ? error.message 
        : 'Failed to connect to server';
      setError(errorMessage);
      onUploadError(errorMessage);
      setIsUploading(false);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      uploadFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: isUploading,
  });

  return (
    <div className="flex-1 flex items-center justify-center bg-background p-6 relative overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-primary/10 dark:bg-primary/15 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-accent/10 dark:bg-accent/15 rounded-full blur-3xl animate-float-delayed" />
      </div>

      <div className="relative z-10 w-full max-w-2xl animate-fade-in-up">
        <div className="glass-card rounded-[2.5rem] p-12 shadow-2xl space-y-8 border border-border/50">
          <div className="text-center space-y-5">
            <div className="w-24 h-24 mx-auto rounded-3xl bg-gradient-to-br from-primary via-accent to-primary flex items-center justify-center shadow-2xl shadow-primary/20 hover-lift ios-scale">
              <FileText className="w-12 h-12 text-white" />
            </div>
            <div>
              <h2 className="text-4xl font-display font-bold gradient-text text-glow mb-3 tracking-tight">Upload Your Document</h2>
              <p className="text-muted-foreground text-lg font-medium">
                Drop your PDF here or click to browse
              </p>
            </div>
          </div>

          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-3xl p-16 text-center ios-transition cursor-pointer ${
              isDragActive
                ? 'border-primary bg-primary/10 dark:bg-primary/5 scale-[1.02] shadow-lg shadow-primary/10'
                : 'border-border hover:border-primary/50 hover:bg-primary/5 dark:hover:bg-primary/10'
            } ${error ? 'border-destructive bg-destructive/5' : ''}`}
          >
            <input {...getInputProps()} />
            <div className="space-y-6">
              <div className={`w-20 h-20 mx-auto rounded-3xl flex items-center justify-center ios-transition shadow-lg ${
                isDragActive 
                  ? 'bg-gradient-to-br from-primary/20 to-accent/20 scale-110' 
                  : 'glass-card hover:scale-105'
              }`}>
                <Upload className={`w-9 h-9 ios-transition ${
                  isDragActive ? 'text-primary animate-bounce-subtle' : 'text-primary'
                }`} />
              </div>
              <div>
                <p className="text-xl font-display font-bold text-foreground mb-2 tracking-tight">
                  {isDragActive ? 'Drop your PDF here' : 'Drag & drop your PDF'}
                </p>
                <p className="text-sm text-muted-foreground font-medium">
                  or click to select a file from your device
                </p>
              </div>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-3 p-5 rounded-2xl glass-card border border-destructive/30 bg-destructive/5 animate-fade-in-up">
              <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0" />
              <p className="text-sm text-destructive font-medium">{error}</p>
            </div>
          )}

          {isUploading && uploadProgress > 0 && (
            <div className="space-y-4 animate-fade-in-up">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground font-semibold flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-primary animate-pulse-glow" />
                  Processing your document...
                </span>
                <span className="text-foreground font-bold text-base">{uploadProgress}%</span>
              </div>
              <div className="h-3 bg-muted/50 rounded-full overflow-hidden backdrop-blur-sm">
                <div
                  className="h-full bg-gradient-to-r from-primary to-accent ios-transition relative"
                  style={{ width: `${uploadProgress}%` }}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
                </div>
              </div>
            </div>
          )}

          <Button
            onClick={() => document.querySelector('input[type="file"]')?.dispatchEvent(new MouseEvent('click'))}
            disabled={isUploading}
            size="lg"
            variant="premium"
            className="w-full text-lg h-16 rounded-2xl ios-scale font-bold tracking-wide"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-5 h-5 mr-3 animate-spin" />
                Processing Document...
              </>
            ) : (
              <>
                <FileText className="w-5 h-5 mr-3" />
                Select PDF File
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
