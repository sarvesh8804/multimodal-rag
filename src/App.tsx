import { useState, useEffect } from 'react';
import { FileText, AlertCircle, CheckCircle, ArrowLeft } from 'lucide-react';
import { PDFUpload } from './components/PDFUpload';
import { PDFViewer } from './components/PDFViewer';
import { ChatInterface } from './components/ChatInterface';
import { ToastContainer } from './components/Toast';
import { LoadingSpinner } from './components/LoadingSpinner';
import { Homepage } from './components/Homepage';
import { ThemeToggle } from './components/ThemeToggle';
import { api, APIError } from './utils/api';
import type { Message, Document, Toast } from './types';

function App() {
  const [showApp, setShowApp] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    if (showApp) {
      checkBackendHealth();
    }
  }, [showApp]);

  const checkBackendHealth = async () => {
    try {
      await api.checkHealth();
      setBackendStatus('online');
      addToast('success', 'Connected to backend successfully');
    } catch (error) {
      setBackendStatus('offline');
      addToast('error', 'Failed to connect to backend. Please ensure the API is running.');
    }
  };

  const addToast = (type: Toast['type'], message: string) => {
    const toast: Toast = {
      id: Date.now().toString(),
      type,
      message,
    };
    setToasts((prev) => [...prev, toast]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const handleUploadSuccess = (docId: string, filename: string) => {
    const newDoc: Document = {
      doc_id: docId,
      filename,
      uploadedAt: new Date(),
    };
    setDocuments((prev) => [...prev, newDoc]);
    setSelectedDoc(newDoc);
    setMessages([]);
    addToast('success', `${filename} uploaded and processed successfully`);
  };

  const handleUploadError = (error: string) => {
    addToast('error', error);
  };

  const handleSendMessage = async (query: string) => {
    if (!selectedDoc) {
      addToast('error', 'Please upload a PDF document first');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsQuerying(true);

    try {
      const response = await api.query(selectedDoc.doc_id, query);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        context: response.context,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage =
        error instanceof APIError
          ? error.message
          : 'Failed to process query. Please try again.';

      addToast('error', errorMessage);

      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your question. Please try again.',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      setIsQuerying(false);
    }
  };

  const retryConnection = () => {
    setBackendStatus('checking');
    checkBackendHealth();
  };

  if (!showApp) {
    return <Homepage onGetStarted={() => setShowApp(true)} />;
  }

  if (backendStatus === 'checking') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <LoadingSpinner message="Connecting to backend..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 flex flex-col transition-colors duration-300">
      <ToastContainer toasts={toasts} onClose={removeToast} />

      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-700 px-6 py-4 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowApp(false)}
              className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-xl transition-colors"
              aria-label="Back to home"
            >
              <ArrowLeft className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center shadow-lg">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">MRAG System</h1>
                <p className="text-xs text-gray-600 dark:text-gray-400">Retrieval-Augmented Generation</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {backendStatus === 'online' ? (
              <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
                <CheckCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Backend Online</span>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
                  <AlertCircle className="w-4 h-4" />
                  <span className="text-sm font-medium">Backend Offline</span>
                </div>
                <button
                  onClick={retryConnection}
                  className="px-3 py-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white text-sm rounded-lg transition-all"
                >
                  Retry
                </button>
              </div>
            )}

            {selectedDoc && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border border-blue-200 dark:border-blue-700 rounded-lg">
                <FileText className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <span className="text-sm text-gray-900 dark:text-gray-300 max-w-[200px] truncate">
                  {selectedDoc.filename}
                </span>
              </div>
            )}

            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-8xl w-full mx-auto flex flex-col p-6 gap-6 overflow-hidden">
        {!selectedDoc ? (
          <div className="flex-1 flex items-center justify-center">
            <PDFUpload
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
              isUploading={isUploading}
              setIsUploading={setIsUploading}
            />
          </div>
        ) : (
          // Two column layout: left = chat, right = pdf viewer (each 50%)
          <div className="flex-1 flex flex-col md:flex-row gap-10 overflow-hidden">
            {/* Left: Chat - match PDF viewer height so bottoms align */}
            <div className="md:w-[58%] w-full h-[calc(100vh-8rem)] bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-2xl overflow-hidden border border-blue-200 dark:border-gray-700">
              <ChatInterface
                messages={messages}
                onSendMessage={handleSendMessage}
                isLoading={isQuerying}
                disabled={backendStatus === 'offline'}
              />
            </div>

            {/* Right: PDF viewer (sticky) */}
            <div className="md:w-[42%] w-full flex-shrink-0">
              <div className="sticky top-20 h-[calc(100vh-8rem)] bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-2xl overflow-hidden border border-blue-200 dark:border-gray-700">
                {selectedDoc && (
                  <PDFViewer docId={selectedDoc.doc_id} filename={selectedDoc.filename} />
                )}
              </div>
            </div>
          </div>
        )}

        {selectedDoc && documents.length > 1 && (
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-lg">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-400 mb-3">
              Available Documents
            </h3>
            <div className="flex gap-2 flex-wrap">
              {documents.map((doc) => (
                <button
                  key={doc.doc_id}
                  onClick={() => {
                    setSelectedDoc(doc);
                    setMessages([]);
                  }}
                  className={`
                    px-3 py-2 rounded-lg text-sm font-medium transition-all duration-300 hover:scale-105
                    ${
                      selectedDoc.doc_id === doc.doc_id
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                        : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                    }
                  `}
                >
                  {doc.filename}
                </button>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
