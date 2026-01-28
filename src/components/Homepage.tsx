import { FileText, MessageSquare, Sparkles, Zap, Shield, Rocket } from 'lucide-react';
import { Button } from '../components/ui/button';
import { ThemeToggle } from '../components/ThemeToggle';

interface HomepageProps {
  onGetStarted: () => void;
}

export function Homepage({ onGetStarted }: HomepageProps) {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden flex-1">
      {/* Animated gradient background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-primary/10 dark:bg-primary/20 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-accent/10 dark:bg-accent/20 rounded-full blur-3xl animate-float-delayed" />
        <div className="absolute top-1/2 left-1/2 w-[400px] h-[400px] bg-primary/5 dark:bg-primary/15 rounded-full blur-3xl animate-float-slow" />
      </div>

      {/* Hero Section */}
      <div className="relative z-10 container mx-auto px-6 pt-32 pb-24">
        <div className="max-w-5xl mx-auto text-center space-y-10 animate-fade-in-up">
          <div className="inline-flex items-center gap-3 px-5 py-2.5 rounded-full glass-card hover-lift ios-scale">
            <Sparkles className="w-5 h-5 text-primary animate-pulse-glow" />
            <span className="text-sm font-semibold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Next-Generation RAG System
            </span>
          </div>
          
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-display font-bold leading-[1.1] tracking-tight">
            <span className="gradient-text text-glow">Transform Documents</span>
            <br />
            <span className="text-foreground">Into Conversations</span>
          </h1>
          
          <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed font-light">
            Upload your PDFs and unlock intelligent conversations. Powered by advanced AI 
            to deliver precise, context-aware answers instantly.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-6">
            <Button 
              onClick={onGetStarted} 
              size="lg"
              variant="premium"
              className="text-lg px-10 h-14 shadow-2xl ios-scale"
            >
              Get Started
              <Sparkles className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="relative z-10 container mx-auto px-6 py-24">
        <div className="max-w-7xl mx-auto grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            {
              icon: <FileText className="w-8 h-8 text-primary" />,
              title: 'PDF Processing',
              description: 'Advanced document parsing with intelligent chunking and indexing'
            },
            {
              icon: <MessageSquare className="w-8 h-8 text-accent" />,
              title: 'Smart Chat',
              description: 'Context-aware conversations that understand your documents'
            },
            {
              icon: <Zap className="w-8 h-8 text-accent" />,
              title: 'Lightning Fast',
              description: 'Instant responses powered by optimized vector search'
            },
            {
              icon: <Shield className="w-8 h-8 text-primary" />,
              title: 'Secure & Private',
              description: 'Your documents stay private with enterprise-grade security'
            },
            {
              icon: <Rocket className="w-8 h-8 text-accent" />,
              title: 'Scalable',
              description: 'From single documents to entire knowledge bases'
            },
            {
              icon: <Sparkles className="w-8 h-8 text-accent" />,
              title: 'AI-Powered',
              description: 'Cutting-edge language models for accurate understanding'
            }
          ].map((feature, index) => (
            <div
              key={index}
              className="glass-card p-8 rounded-3xl hover-lift ios-scale group cursor-pointer animate-fade-in-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 dark:from-primary/20 dark:to-accent/20 flex items-center justify-center mb-6 group-hover:scale-110 ios-transition border border-primary/10">
                {feature.icon}
              </div>
              <h3 className="text-2xl font-display font-bold text-foreground mb-3">
                {feature.title}
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Tech Stack Section */}
      <div className="relative z-10 container mx-auto px-6 pb-24">
        <div className="max-w-4xl mx-auto glass-card rounded-[2.5rem] p-12 md:p-16 text-center border border-primary/10 hover:border-primary/20 ios-transition">
          <div className="inline-flex items-center gap-2 px-4 py-2 glass-card rounded-full mb-6">
            <Sparkles className="w-4 h-4 text-primary animate-pulse-glow" />
            <span className="text-xs font-semibold text-foreground/70 uppercase tracking-wider">
              Technology Stack
            </span>
          </div>
          <h2 className="font-display text-4xl md:text-5xl font-bold mb-6 gradient-text">
            Built with Enterprise-Grade Technology
          </h2>
          <p className="text-muted-foreground text-lg mb-10 max-w-2xl mx-auto font-light">
            Leveraging state-of-the-art AI models, vector databases, and 
            natural language processing to deliver unparalleled accuracy.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            {['GPT-4', 'Vector Embeddings', 'Semantic Search', 'RAG Architecture', 'Real-time Processing', 'Enterprise Security'].map((tech) => (
              <div
                key={tech}
                className="px-6 py-3 glass-card rounded-2xl text-sm font-semibold text-foreground hover:border-primary/40 hover:bg-primary/5 dark:hover:bg-primary/10 ios-transition hover-lift ios-scale"
              >
                {tech}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
