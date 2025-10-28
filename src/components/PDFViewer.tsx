
interface PDFViewerProps {
  docId: string;
  filename: string;
}

export function PDFViewer({ docId, filename }: PDFViewerProps) {
  // The backend stores uploaded files as uploads/{docId}_{filename}
  const safeUrl = `http://localhost:8000/uploads/${encodeURIComponent(docId + '_' + filename)}`;

  return (
    <div className="h-full w-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 dark:border-gray-700 bg-white/60 dark:bg-gray-800/60">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-semibold text-gray-800 dark:text-gray-200">{filename}</h3>
          <a
            href={safeUrl}
            target="_blank"
            rel="noreferrer"
            className="text-xs text-blue-600 dark:text-blue-400 underline"
          >
            Open raw
          </a>
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-400">Preview</div>
      </div>

      <div className="flex-1 overflow-auto">
        <iframe
          title={`pdf-${docId}`}
          src={safeUrl}
          className="w-full h-full"
        />
      </div>
    </div>
  );
}