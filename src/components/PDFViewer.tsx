import { ExternalLink, FileText } from 'lucide-react';
import { Button } from '../components/ui/button';

interface PDFViewerProps {
  docId: string;
  filename: string;
}

export function PDFViewer({ docId, filename }: PDFViewerProps) {
  const safeUrl = `http://localhost:8000/uploads/${encodeURIComponent(docId + '_' + filename)}`;

  return (
    <div className="h-full w-full flex flex-col bg-background/30">
      {/* Header */}
      <div className="flex items-center justify-between px-8 py-5 border-b border-border glass-border">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center border border-primary/30">
            <FileText className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h3 className="font-display text-base font-semibold text-foreground">{filename}</h3>
            <p className="text-xs text-muted-foreground font-medium">Active Document</p>
          </div>
        </div>
        <Button
          variant="outline"
          size="sm"
          asChild
          className="gap-2 font-display"
        >
          <a
            href={safeUrl}
            target="_blank"
            rel="noreferrer"
          >
            <ExternalLink className="w-4 h-4" />
            Open External
          </a>
        </Button>
      </div>

      {/* PDF Viewer */}
      <div className="flex-1 overflow-hidden bg-muted/5 backdrop-blur-sm">
        <iframe
          title={`pdf-${docId}`}
          src={safeUrl}
          className="w-full h-full border-0"
        />
      </div>
    </div>
  );
}
