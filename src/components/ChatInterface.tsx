// import { useState, useRef, useEffect } from 'react';
// import { Send, Loader2, User, Bot } from 'lucide-react';
// import type { Message } from '../types';

// interface ChatInterfaceProps {
//   messages: Message[];
//   onSendMessage: (message: string) => void;
//   isLoading: boolean;
//   disabled: boolean;
// }

// export function ChatInterface({
//   messages,
//   onSendMessage,
//   isLoading,
//   disabled,
// }: ChatInterfaceProps) {
//   const [input, setInput] = useState('');
//   const messagesEndRef = useRef<HTMLDivElement>(null);
//   const inputRef = useRef<HTMLTextAreaElement>(null);

//   useEffect(() => {
//     messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//   }, [messages]);

//   const handleSubmit = (e: React.FormEvent) => {
//     e.preventDefault();
//     if (input.trim() && !disabled && !isLoading) {
//       onSendMessage(input.trim());
//       setInput('');
//       inputRef.current?.focus();
//     }
//   };

//   const handleKeyDown = (e: React.KeyboardEvent) => {
//     if (e.key === 'Enter' && !e.shiftKey) {
//       e.preventDefault();
//       handleSubmit(e);
//     }
//   };

//   return (
//     <div className="flex flex-col h-full">
//       <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
//         {messages.length === 0 ? (
//           <div className="flex flex-col items-center justify-center h-full text-center px-4">
//             <div className="w-20 h-20 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center mb-4 shadow-lg">
//               <Bot className="w-10 h-10 text-white" />
//             </div>
//             <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
//               MRAG Assistant
//             </h2>
//             <p className="text-gray-600 dark:text-gray-400 max-w-md">
//               Upload a PDF document and start asking questions. I'll retrieve relevant
//               information and provide detailed answers.
//             </p>
//           </div>
//         ) : (
//           <>
//             {messages.map((message) => (
//               <div
//                 key={message.id}
//                 className={`flex gap-3 ${
//                   message.role === 'user' ? 'justify-end' : 'justify-start'
//                 }`}
//               >
//                 {message.role === 'assistant' && (
//                   <div className="w-8 h-8 rounded-full bg-gradient-to-r from-green-500 to-emerald-500 flex items-center justify-center flex-shrink-0 mt-1 shadow-md">
//                     <Bot className="w-5 h-5 text-white" />
//                   </div>
//                 )}

//                 <div
//                   className={`
//                     max-w-[75%] rounded-2xl px-4 py-3 shadow-lg animate-fade-in
//                     ${
//                       message.role === 'user'
//                         ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
//                         : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700'
//                     }
//                   `}
//                 >
//                   <div className="flex items-center gap-2 mb-1">
//                     <span className="text-xs font-semibold opacity-80">
//                       {message.role === 'user' ? 'You' : 'Assistant'}
//                     </span>
//                     <span className="text-xs opacity-60">
//                       {message.timestamp.toLocaleTimeString([], {
//                         hour: '2-digit',
//                         minute: '2-digit',
//                       })}
//                     </span>
//                   </div>
//                   <p className="text-sm leading-relaxed whitespace-pre-wrap">
//                     {message.content}
//                   </p>
//                   {message.context && message.context.length > 0 && (
//                     <div className="mt-3 pt-3 border-t border-gray-700">
//                       <p className="text-xs font-semibold opacity-80 mb-2">
//                         Sources:
//                       </p>
//                       <div className="space-y-1">
//                         {message.context.map((ctx, idx) => (
//                           <div
//                             key={idx}
//                             className="text-xs opacity-70 bg-gray-700/50 rounded px-2 py-1"
//                           >
//                             Page {ctx.page}
//                           </div>
//                         ))}
//                       </div>
//                     </div>
//                   )}
//                 </div>

//                 {message.role === 'user' && (
//                   <div className="w-8 h-8 rounded-full bg-gradient-to-r from-pink-500 to-orange-500 flex items-center justify-center flex-shrink-0 mt-1 shadow-md">
//                     <User className="w-5 h-5 text-white" />
//                   </div>
//                 )}
//               </div>
//             ))}

//             {isLoading && (
//               <div className="flex gap-3 justify-start">
//                 <div className="w-8 h-8 rounded-full bg-gradient-to-r from-green-500 to-emerald-500 flex items-center justify-center flex-shrink-0 mt-1 shadow-md">
//                   <Bot className="w-5 h-5 text-white" />
//                 </div>
//                 <div className="bg-white dark:bg-gray-800 rounded-2xl px-4 py-3 shadow-lg border border-gray-200 dark:border-gray-700">
//                   <div className="flex items-center gap-2">
//                     <Loader2 className="w-4 h-4 text-purple-600 dark:text-purple-400 animate-spin" />
//                     <span className="text-sm text-gray-700 dark:text-gray-400">Thinking...</span>
//                   </div>
//                 </div>
//               </div>
//             )}

//             <div ref={messagesEndRef} />
//           </>
//         )}
//       </div>

//       <div className="border-t border-gray-200 dark:border-gray-800 p-4 bg-gray-50 dark:bg-gray-900/50">
//         <form onSubmit={handleSubmit} className="flex gap-3">
//           <textarea
//             ref={inputRef}
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             onKeyDown={handleKeyDown}
//             placeholder={
//               disabled
//                 ? 'Upload a PDF to start chatting...'
//                 : 'Ask a question about your document...'
//             }
//             disabled={disabled || isLoading}
//             rows={1}
//             className="flex-1 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed resize-none max-h-32 border border-gray-300 dark:border-gray-700 transition-all"
//           />
//           <button
//             type="submit"
//             disabled={disabled || isLoading || !input.trim()}
//             className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all duration-300 flex items-center gap-2 shadow-lg hover:shadow-xl hover:scale-105"
//           >
//             {isLoading ? (
//               <Loader2 className="w-5 h-5 animate-spin" />
//             ) : (
//               <Send className="w-5 h-5" />
//             )}
//           </button>
//         </form>
//       </div>
//     </div>
//   );
// }

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, User, Bot, Zap } from 'lucide-react';

// NOTE: Assuming Message type includes id, role ('user' | 'assistant'), content, timestamp, and optional context.
interface ContextItem {
  page: number;
}
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  context?: ContextItem[];
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  disabled: boolean;
}

export function ChatInterface({
  messages,
  onSendMessage,
  isLoading,
  disabled,
}: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const MessageBubble = ({ message }: { message: Message }) => {
    const isUser = message.role === 'user';

    // 🌟 UPDATED: User bubble style (Cyan/Blue gradient - cool, techy color)
    const userStyle = 'bg-gradient-to-br from-blue-700 to-cyan-500 text-white rounded-tr-xl rounded-bl-xl shadow-lg shadow-blue-500/30 border border-cyan-400/50';

    // Assistant bubble style (Metallic, systemic look with Neon Green accents)
    const assistantStyle = 'metallic-card rounded-tl-xl rounded-br-xl border border-neon-green/30 text-gray-100 shadow-xl shadow-neon-green/10';

    const avatar = (
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1 shadow-lg ${
          // 🌟 UPDATED: User avatar to a solid dark/metallic blue circle
          isUser ? 'bg-blue-600 border border-cyan-400' : 'bg-neon-green/20 border border-neon-green/50'
        }`}
      >
        {/* 🌟 UPDATED: User icon color to Cyan for consistency */}
        {isUser ? <User className="w-5 h-5 text-cyan-400" /> : <Bot className="w-5 h-5 text-neon-green" />}
      </div>
    );

    return (
      <div
        className={`flex gap-3 animate-fade-in ${
          isUser ? 'justify-end' : 'justify-start'
        }`}
      >
        {!isUser && avatar}

        <div
          className={`
            max-w-[75%] px-4 py-3 transition-all duration-300
            ${isUser ? userStyle : assistantStyle}
          `}
        >
          <div className="flex items-center gap-2 mb-1">
            {/* 🌟 UPDATED: User Role Name */}
            <span className={`text-xs font-bold ${!isUser ? 'text-neon-green neon-text-glow' : 'text-cyan-200'}`}>
              {isUser ? 'OPERATOR INTERFACE' : 'RAG CORE'}
            </span>
            <span className="text-xs opacity-60">
              {message.timestamp.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          </div>
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>

          {/* Context/Source Display (Neon Green/Cyan theme) */}
          {message.context && message.context.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-700/50">
              <p className="text-xs font-semibold text-cyan-400 mb-2">
                <Zap className='w-3 h-3 inline mr-1'/> Data Trace:
              </p>
              <div className="space-y-1">
                {message.context.map((ctx, idx) => (
                  <div
                    key={idx}
                    className="text-xs font-mono text-neon-green opacity-80 bg-gray-900/50 rounded-lg px-2 py-1 border border-neon-green/20 transition-all hover:bg-gray-800"
                  >
                    //PAGE-ID: {ctx.page}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {isUser && avatar}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-neon-black/50 backdrop-blur-sm rounded-xl border border-gray-700 shadow-2xl shadow-neon-green/10">
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 scrollbar-thin scrollbar-thumb-neon-green/50 scrollbar-track-gray-900/50">
        {messages.length === 0 ? (
          // Empty State (Refined)
          <div className="flex flex-col items-center justify-center h-full text-center px-4 pt-16">
            <div className="w-24 h-24 rounded-full bg-cyan-500/10 border-4 border-cyan-400/50 flex items-center justify-center mb-6 shadow-2xl shadow-cyan-400/30 animate-pulse-slow">
              <Bot className="w-12 h-12 text-cyan-400 neon-text-glow" />
            </div>
            <h2 className="text-3xl font-extrabold text-white mb-2 neon-text-glow">
              RAG ASSISTANT // STANDBY
            </h2>
            <p className="text-gray-400 max-w-lg text-sm font-mono border-t border-b border-gray-700/50 py-2">
              System awaits document ingestion. Once vector encoding is complete,
              initiate query protocols for grounded, context-aware information retrieval.
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}

            {/* Loading/Typing Indicator */}
            {isLoading && (
              <div className="flex gap-3 justify-start animate-pulse">
                <div className="w-8 h-8 rounded-full bg-neon-green/20 border border-neon-green/50 flex items-center justify-center flex-shrink-0 mt-1 shadow-md">
                  <Bot className="w-5 h-5 text-neon-green" />
                </div>
                <div className="metallic-card rounded-2xl px-4 py-3 border border-neon-green/30">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 text-neon-green animate-spin" />
                    <span className="text-sm text-neon-green neon-text-glow-sm">PROCESSING QUERY...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Form Area (Metallic Card) */}
      <div className="p-4 metallic-card border-t border-gray-700/50">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              disabled
                ? '[[SYSTEM LOCK: Awaiting Document Ingestion...]]'
                : 'Enter query for RAG core...'
            }
            disabled={disabled || isLoading}
            rows={1}
            // Styled textarea: dark background, neon focus ring
            className="flex-1 bg-gray-900/80 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed resize-none max-h-40 border border-gray-700 placeholder-gray-500 font-mono transition-all duration-200"
          />
          <button
            type="submit"
            disabled={disabled || isLoading || !input.trim()}
            // Send Button: Neon Green/Cyan Primary Action
            className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-neon-green hover:from-cyan-400 hover:to-neon-green text-neon-black rounded-xl font-bold transition-all duration-300 flex items-center gap-2 shadow-xl shadow-cyan-500/20 hover:shadow-neon-light disabled:bg-gray-700 disabled:from-gray-700 disabled:to-gray-600 disabled:text-gray-400 disabled:shadow-none"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin text-neon-black" />
            ) : (
              <Send className="w-5 h-5" />
            )}
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
      </div>
    </div>
  );
}