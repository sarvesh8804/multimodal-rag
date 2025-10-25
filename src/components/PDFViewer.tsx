import { ExternalLink, FileText } from 'lucide-react'; // Added ExternalLink and FileText for icons

interface PDFViewerProps {
  docId: string;
  filename: string;
}

export function PDFViewer({ docId, filename }: PDFViewerProps) {
  // The backend stores uploaded files as uploads/{docId}_{filename}
  const safeUrl = `http://localhost:8000/uploads/${encodeURIComponent(docId + '_' + filename)}`;

  return (
    // Main container uses a metallic card style with a dark background
    <div className="h-full w-full flex flex-col metallic-card rounded-xl border border-gray-700 shadow-xl overflow-hidden">
      
      {/* Header Bar: Replaced standard border/background with a neon-tech look */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-neon-green/30 bg-card-highlight shadow-inner shadow-neon-green/10">
        <div className="flex items-center gap-3">
          
          {/* File icon and filename with neon glow */}
          <FileText className="w-5 h-5 text-neon-green neon-text-glow" />
          <h3 className="text-sm font-semibold text-white truncate max-w-xs">{filename}</h3>
          
          {/* 'Open raw' link styled with a neon accent */}
          <a
            href={safeUrl}
            target="_blank"
            rel="noreferrer"
            className="text-xs text-cyan-400 hover:text-white transition-colors flex items-center gap-1 group"
            title="Open raw document in a new tab"
          >
            Open Raw
            <ExternalLink className="w-3 h-3 group-hover:scale-110 transition-transform" />
          </a>
        </div>
        
        {/* Status indicator, styled as a metallic label */}
        <div className="text-xs font-mono text-gray-400 px-2 py-1 rounded-full border border-gray-600 bg-gray-800/50">
          DOCUMENT PREVIEW
        </div>
      </div>

      {/* Iframe Container: Flex-1 to fill remaining space, ensures scrollbar is correct */}
      <div className="flex-1 overflow-auto bg-neon-black p-2">
        {/* The iframe itself */}
        <iframe
          title={`pdf-${docId}`}
          src={safeUrl}
          // The iframe should be styled to blend seamlessly with the dark background
          className="w-full h-full border border-gray-800 rounded-lg shadow-inner"
          // Add sandbox attributes for security best practice, though not style-related
          sandbox="allow-scripts allow-same-origin allow-popups allow-forms allow-presentation"
        />
      </div>
    </div>
  );
}