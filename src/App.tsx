
// import { useState, useEffect } from 'react';
// import { FileText, AlertCircle, CheckCircle, ArrowLeft } from 'lucide-react';
// import { PDFUpload } from './components/PDFUpload';
// import { PDFViewer } from './components/PDFViewer';
// import { ChatInterface } from './components/ChatInterface';
// import { ToastContainer } from './components/Toast';
// import { LoadingSpinner } from './components/LoadingSpinner';
// import { Homepage } from './components/Homepage';
// import { ThemeToggle } from './components/ThemeToggle';
// import { api, APIError } from './utils/api';
// import type { Message, Document, Toast } from './types';

// export function App() {
//   const [showApp, setShowApp] = useState(false);
//   const [documents, setDocuments] = useState<Document[]>([]);
//   const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
//   const [messages, setMessages] = useState<Message[]>([]);
//   const [toasts, setToasts] = useState<Toast[]>([]);
//   const [isUploading, setIsUploading] = useState(false);
//   const [isQuerying, setIsQuerying] = useState(false);
//   const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

//   useEffect(() => {
//     if (showApp) checkBackendHealth();
//   }, [showApp]);

//   const checkBackendHealth = async () => {
//     try {
//       await api.checkHealth();
//       setBackendStatus('online');
//       addToast('success', 'Connected to backend successfully');
//     } catch {
//       setBackendStatus('offline');
//       addToast('error', 'Failed to connect to backend. Please ensure the API is running.');
//     }
//   };

//   const addToast = (type: Toast['type'], message: string) => {
//     const toast: Toast = { id: Date.now().toString(), type, message };
//     setToasts((prev) => [...prev, toast]);
//   };

//   const removeToast = (id: string) => setToasts((prev) => prev.filter((t) => t.id !== id));

//   const handleMetrics = () => {
    
//   }

//   const handleUploadSuccess = (docId: string, filename: string) => {
//     const newDoc: Document = { doc_id: docId, filename, uploadedAt: new Date() };
//     setDocuments((prev) => [...prev, newDoc]);
//     setSelectedDoc(newDoc);
//     setMessages([]);
//     addToast('success', `${filename} uploaded and processed successfully`);
//   };

//   const handleUploadError = (error: string) => addToast('error', error);

//   const handleSendMessage = async (query: string) => {
//     if (!selectedDoc) return addToast('error', 'Please upload a PDF document first');

//     const userMessage: Message = { id: Date.now().toString(), role: 'user', content: query, timestamp: new Date() };
//     setMessages((prev) => [...prev, userMessage]);
//     setIsQuerying(true);

//     try {
//       const response = await api.query(selectedDoc.doc_id, query);
//       const assistantMessage: Message = {
//         id: (Date.now() + 1).toString(),
//         role: 'assistant',
//         content: response.answer,
//         timestamp: new Date(),
//         context: response.context,
//       };
//       setMessages((prev) => [...prev, assistantMessage]);
//     } catch (error) {
//       const errorMsg = error instanceof APIError ? error.message : 'Failed to process query.';
//       addToast('error', errorMsg);
//       setMessages((prev) => [
//         ...prev,
//         { id: (Date.now() + 1).toString(), role: 'assistant', content: 'Error processing question.', timestamp: new Date() },
//       ]);
//     } finally {
//       setIsQuerying(false);
//     }
//   };

//   const retryConnection = () => { setBackendStatus('checking'); checkBackendHealth(); };

//   if (!showApp) return <Homepage onGetStarted={() => setShowApp(true)} />;

//   if (backendStatus === 'checking')
//     return (
//       <div className="min-h-screen flex items-center justify-center bg-neon-black">
//         <LoadingSpinner message="Connecting to backend..." />
//       </div>
//     );

//   return (
//     <div className="min-h-screen bg-neon-black text-white flex flex-col transition-colors duration-300">
//       <ToastContainer toasts={toasts} onClose={removeToast} />

//       {/* HEADER */}
//       <header className="bg-card-surface/80 backdrop-blur-lg border-b border-neon-green/30 px-6 py-4 flex justify-between items-center shadow-neon-light">
//         <div className="flex items-center gap-4">
//           <button
//             onClick={() => setShowApp(false)}
//             className="p-2 hover:bg-neon-green/20 rounded-xl transition-all shadow-neon-light"
//           >
//             <ArrowLeft className="w-5 h-5 text-neon-green" />
//           </button>
//           <div className="flex items-center gap-3">
//             <div className="w-10 h-10 rounded-xl bg-gradient-to-r from-neon-green to-cyan-400 flex items-center justify-center shadow-neon-light">
//               <FileText className="w-6 h-6 text-black" />
//             </div>
//             <div>
//               <h1 className="text-xl font-bold neon-text-glow">MRAG System</h1>
//               <p className="text-sm text-gray-400">Retrieval-Augmented Generation</p>
//             </div>
//           </div>
//         </div>

//         <div className="flex items-center gap-4">
//           {backendStatus === 'online' ? (
//             <div className="flex items-center gap-2 text-neon-green">
//               <CheckCircle className="w-4 h-4" />
//               <span className="text-sm font-medium">Backend Online</span>
//             </div>
//           ) : (
//             <div className="flex items-center gap-3">
//               <div className="flex items-center gap-2 text-red-600">
//                 <AlertCircle className="w-4 h-4" />
//                 <span className="text-sm font-medium">Backend Offline</span>
//               </div>
//               <button
//                 onClick={retryConnection}
//                 className="px-3 py-1 bg-neon-green text-black rounded-lg shadow-neon-light hover:scale-105 transition-all"
//               >
//                 Retry
//               </button>
//             </div>
//           )}

//           {selectedDoc && (
//             <div className="flex items-center gap-2 px-3 py-1.5 bg-card-surface/50 border border-neon-green rounded-lg shadow-neon-light">
//               <FileText className="w-4 h-4 text-neon-green" />
//               <span className="text-sm truncate max-w-[200px]">{selectedDoc.filename}</span>
//             </div>
//           )}

//           {/* <ThemeToggle /> */}
//         </div>
//       </header>

//       {/* MAIN */}
//       <main className="flex-1 max-w-8xl mx-auto p-6 gap-6 flex flex-col overflow-hidden">
//         {!selectedDoc ? (
//           <div className="flex-1 flex items-center justify-center">
//             <PDFUpload
//               onUploadSuccess={handleUploadSuccess}
//               onUploadError={handleUploadError}
//               isUploading={isUploading}
//               setIsUploading={setIsUploading}
//             />
//           </div>
//         ) : (
//           <div className="flex-1 flex md:flex-row flex-col gap-10 overflow-hidden">
//             {/* Chat */}
//             <div className="md:w-[58%] w-full h-[calc(100vh-8rem)] bg-card-surface/50 rounded-2xl shadow-2xl border border-neon-green overflow-hidden">
//               <ChatInterface
//                 messages={messages}
//                 onSendMessage={handleSendMessage}
//                 isLoading={isQuerying}
//                 disabled={backendStatus === 'offline'}
//               />
//             </div>

//             {/* PDF Viewer */}
//             <div className="md:w-[42%] w-full flex-shrink-0">
//               <div className="sticky top-20 h-[calc(100vh-8rem)] bg-card-surface/50 rounded-2xl shadow-2xl border border-neon-green overflow-hidden">
//                 {selectedDoc && <PDFViewer docId={selectedDoc.doc_id} filename={selectedDoc.filename} />}
//               </div>
//             </div>
//           </div>
//         )}

//         {/* Document List */}
//         {selectedDoc && documents.length > 1 && (
//           <div className="bg-card-surface/50 rounded-xl p-4 border border-neon-green shadow-neon-light">
//             <h3 className="text-sm font-semibold text-gray-400 mb-3">Available Documents</h3>
//             <div className="flex gap-2 flex-wrap">
//               {documents.map((doc) => (
//                 <button
//                   key={doc.doc_id}
//                   onClick={() => { setSelectedDoc(doc); setMessages([]); }}
//                   className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-300 shadow-neon-light ${
//                     selectedDoc.doc_id === doc.doc_id
//                       ? 'bg-neon-green text-black shadow-lg'
//                       : 'bg-card-surface text-gray-200 hover:bg-neon-green/20'
//                   }`}
//                 >
//                   {doc.filename}
//                 </button>
//               ))}
//             </div>
//             <button onClick={handleMetrics} >view metrics</button>
//           </div>
//         )}
//       </main>
//     </div>
//   );
// }

// export default App;


import { Toaster } from "./components/ui/toaster";
import { Toaster as Sonner } from "./components/ui/sonner";
import { TooltipProvider } from "./components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
