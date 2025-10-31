import { useState } from 'react';
import { Homepage } from '../components/Homepage';
import { ChatInterface } from '../components/ChatInterface';
import { PDFUpload } from '../components/PDFUpload';
import { PDFViewer } from '../components/PDFViewer';
import { ToastContainer } from '../components/Toast';
import { ThemeToggle } from '../components/ThemeToggle';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Toast {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}

const Index = () => {
  const [showHomepage, setShowHomepage] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [docId, setDocId] = useState<string | null>(null);
  const [filename, setFilename] = useState<string>('');
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (type: Toast['type'], message: string) => {
    const id = Date.now().toString();
    setToasts((prev) => [...prev, { id, type, message }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  const handleGetStarted = () => {
    setShowHomepage(false);
  };

  const handleUploadSuccess = (uploadedDocId: string, uploadedFilename: string) => {
    setDocId(uploadedDocId);
    setFilename(uploadedFilename);
    addToast('success', 'Document uploaded successfully!');
  };

  const handleUploadError = (error: string) => {
    addToast('error', error);
  };

  const handleSendMessage = async (messageText: string) => {
    if (!docId) {
      addToast('error', 'Please upload a document first');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          doc_id: docId,
          query: messageText,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer || 'No response received',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      addToast('error', error instanceof Error ? error.message : 'Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-background ios-transition">
      <ThemeToggle />
      <ToastContainer toasts={toasts} onClose={removeToast} />
      
      {showHomepage ? (
        <Homepage onGetStarted={handleGetStarted} />
      ) : !docId ? (
      
        <PDFUpload
          onUploadSuccess={handleUploadSuccess}
          onUploadError={handleUploadError}
          isUploading={isUploading}
          setIsUploading={setIsUploading}
        />
      ) : (
        <div className="flex-1 grid lg:grid-cols-2 gap-px bg-border overflow-hidden">
          <div className="bg-background overflow-hidden">
            <PDFViewer docId={docId} filename={filename} />
          </div>
          <div className="bg-background overflow-hidden">
            <ChatInterface
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              disabled={false}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Index;
