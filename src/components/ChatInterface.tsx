import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, User, Bot, MessageSquare } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Textarea } from '../components/ui/textarea';
import { LoadingSpinner } from './LoadingSpinner';
import type { Message } from './../types';
import ReactMarkdown from 'react-markdown';

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  disabled: boolean;
}

export function ChatInterface({ messages, onSendMessage, isLoading, disabled }: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input);
      setInput('');
    }
  };

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="glass-card border-b border-border px-6 py-5 backdrop-blur-2xl">
        <div className="flex items-center gap-3 animate-fade-in-up">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-primary via-accent to-primary flex items-center justify-center shadow-lg shadow-primary/20 ios-scale">
            <Sparkles className="w-5 h-5 text-white animate-pulse-glow" />
          </div>
          <div>
            <h2 className="text-lg font-display font-bold text-foreground tracking-tight">AI Assistant</h2>
            <p className="text-sm text-muted-foreground font-medium">Ask anything about your document</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center space-y-6 max-w-md animate-fade-in-up px-4">
              <div className="w-20 h-20 mx-auto rounded-3xl glass-card flex items-center justify-center shadow-lg hover-lift">
                <MessageSquare className="w-10 h-10 text-primary" />
              </div>
              <div>
                <h3 className="text-2xl font-display font-bold text-foreground mb-3 tracking-tight">Start a Conversation</h3>
                <p className="text-muted-foreground text-base leading-relaxed">
                  Ask questions about your document and get instant, accurate answers powered by AI.
                </p>
              </div>
              <div className="flex flex-wrap gap-2 justify-center pt-2">
                {['What is this about?', 'Summarize this', 'Key points?'].map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(prompt)}
                    className="glass-card px-4 py-2 rounded-xl text-sm text-foreground hover-lift ios-scale"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <div
                key={message.id}
                className={`flex gap-4 ${
                  message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                } animate-fade-in-up`}
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div
                  className={`w-11 h-11 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-lg ios-scale ${
                    message.role === 'user'
                      ? 'bg-gradient-to-br from-primary to-accent shadow-primary/20'
                      : 'bg-gradient-to-br from-accent to-primary shadow-accent/20'
                  }`}
                >
                  {message.role === 'user' ? (
                    <User className="w-5 h-5 text-white" />
                  ) : (
                    <Bot className="w-5 h-5 text-white" />
                  )}
                </div>
                <div
                  className={`flex-1 max-w-[80%] ${
                    message.role === 'user' ? 'text-right' : 'text-left'
                  }`}
                >
                  <div
                    className={`inline-block px-6 py-4 rounded-3xl ios-transition ${
                      message.role === 'user'
                        ? 'bg-gradient-to-br from-primary to-accent text-white shadow-lg shadow-primary/20'
                        : 'glass-card text-foreground border border-border/50'
                    }`}
                  >
                    <div className="text-sm md:text-base leading-relaxed font-medium markdown-content">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2 px-3 font-medium">
                    {message.timestamp.toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
        {isLoading && (
          <div className="flex gap-4 animate-fade-in-up">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-accent to-primary flex items-center justify-center shadow-lg ios-scale">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="glass-card px-6 py-4 rounded-3xl border border-border/50">
              <LoadingSpinner message="Thinking..." />
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="glass-card border-t border-border p-6 backdrop-blur-2xl">
        <form onSubmit={handleSubmit} className="flex gap-4">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your document..."
            className="flex-1 min-h-[60px] max-h-[120px] resize-none glass-card focus:border-primary/50 ios-transition text-base"
            disabled={disabled}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <Button
            type="submit"
            size="lg"
            disabled={!input.trim() || disabled}
            className="self-end rounded-2xl px-8 ios-scale"
            variant="premium"
          >
            <Send className="w-5 h-5" />
          </Button>
        </form>
        <p className="text-xs text-muted-foreground mt-3 text-center font-medium">
          Press Enter to send, Shift + Enter for new line
        </p>
      </div>
    </div>
  );
}
