// import { ArrowRight, Sparkles, Zap, Shield, FileText } from 'lucide-react';
// import { useTheme } from '../contexts/ThemeContext';
// import { ThemeToggle } from './ThemeToggle';

// interface HomepageProps {
//   onGetStarted: () => void;
// }

// export function Homepage({ onGetStarted }: HomepageProps) {
//   // useTheme is still available; we only need the toggle component here.
//   useTheme();

//   return (
//     <div className="min-h-screen overflow-hidden">
//       <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10 dark:from-blue-900/20 dark:via-purple-900/20 dark:to-pink-900/20" />

//       <div className="absolute inset-0 overflow-hidden pointer-events-none">
//         <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/30 dark:bg-blue-400/20 rounded-full blur-3xl animate-float" />
//         <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-purple-500/30 dark:bg-purple-400/20 rounded-full blur-3xl animate-float-delayed" />
//         <div className="absolute bottom-1/4 left-1/3 w-96 h-96 bg-pink-500/30 dark:bg-pink-400/20 rounded-full blur-3xl animate-float-slow" />
//       </div>

//       <div className="relative z-10 max-w-7xl mx-auto px-6 py-20">
//         <div className="text-center mb-16 animate-slide-up relative">
//           <div className="absolute top-0 right-0 mt-6 mr-6 z-20">
//             <ThemeToggle />
//           </div>
//           <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500/10 to-purple-500/10 dark:from-blue-500/20 dark:to-purple-500/20 rounded-full border border-blue-500/20 dark:border-blue-400/20 mb-6">
//             <Sparkles className="w-4 h-4 text-blue-600 dark:text-blue-400" />
//             <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
//               Powered by AI & Vector Search
//             </span>
//           </div>

//           <h1 className="text-6xl md:text-7xl font-bold mb-6 leading-tight">
//             <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 dark:from-blue-400 dark:via-purple-400 dark:to-pink-400 bg-clip-text text-transparent animate-gradient">
//               Multi-Modal RAG
//             </span>
//             <br />
//             <span className="text-gray-900 dark:text-white">
//               System
//             </span>
//           </h1>

//           <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-12 leading-relaxed">
//             Upload your PDF documents and interact with them using advanced
//             retrieval-augmented generation. Get accurate answers with context
//             from your documents in seconds.
//           </p>

//           <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
//             <button
//               onClick={onGetStarted}
//               className="group px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-2xl font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 flex items-center gap-2"
//             >
//               Get Started
//               <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
//             </button>
//             <button
//               onClick={() => {
//                 document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
//               }}
//               className="px-8 py-4 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm hover:bg-white dark:hover:bg-gray-800 text-gray-900 dark:text-white rounded-2xl font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 border border-gray-200 dark:border-gray-700"
//             >
//               Learn More
//             </button>
//           </div>
//         </div>

//         <div className="relative max-w-5xl mx-auto mb-20 animate-slide-up-delayed">
//           <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-3xl blur-2xl opacity-20" />
//           <div className="relative bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
//             <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-4 flex items-center gap-2">
//               <div className="flex gap-2">
//                 <div className="w-3 h-3 rounded-full bg-red-400" />
//                 <div className="w-3 h-3 rounded-full bg-yellow-400" />
//                 <div className="w-3 h-3 rounded-full bg-green-400" />
//               </div>
//               <span className="text-white text-sm font-medium ml-4">
//                 MRAG System Interface
//               </span>
//             </div>
//             <div className="p-8 grid md:grid-cols-2 gap-6">
//               <div className="space-y-4">
//                 <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-2xl p-6 border border-blue-200 dark:border-blue-700">
//                   <FileText className="w-8 h-8 text-blue-600 dark:text-blue-400 mb-3" />
//                   <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
//                     Upload Documents
//                   </h3>
//                   <p className="text-sm text-gray-600 dark:text-gray-300">
//                     Drag and drop your PDF files
//                   </p>
//                 </div>
//                 <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-2xl p-6 border border-purple-200 dark:border-purple-700">
//                   <Zap className="w-8 h-8 text-purple-600 dark:text-purple-400 mb-3" />
//                   <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
//                     Ask Questions
//                   </h3>
//                   <p className="text-sm text-gray-600 dark:text-gray-300">
//                     Get instant AI-powered answers
//                   </p>
//                 </div>
//               </div>
//               <div className="bg-gradient-to-br from-pink-50 to-blue-50 dark:from-pink-900/20 dark:to-blue-900/20 rounded-2xl p-6 border border-pink-200 dark:border-pink-700 flex items-center justify-center">
//                 <div className="text-center">
//                   <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl mx-auto mb-4 flex items-center justify-center animate-pulse">
//                     <Sparkles className="w-8 h-8 text-white" />
//                   </div>
//                   <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
//                     AI Processing in Action
//                   </p>
//                 </div>
//               </div>
//             </div>
//           </div>
//         </div>

//         <div id="features" className="grid md:grid-cols-3 gap-8 mb-20">
//           {[
//             {
//               icon: Zap,
//               title: 'Lightning Fast',
//               description: 'Get instant responses powered by advanced vector search and AI models',
//               gradient: 'from-blue-500 to-cyan-500',
//               bgGradient: 'from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20',
//               borderColor: 'border-blue-200 dark:border-blue-700',
//             },
//             {
//               icon: Shield,
//               title: 'Secure & Private',
//               description: 'Your documents are processed securely with enterprise-grade encryption',
//               gradient: 'from-purple-500 to-pink-500',
//               bgGradient: 'from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20',
//               borderColor: 'border-purple-200 dark:border-purple-700',
//             },
//             {
//               icon: Sparkles,
//               title: 'Context-Aware',
//               description: 'Retrieves relevant context from your documents for accurate answers',
//               gradient: 'from-pink-500 to-orange-500',
//               bgGradient: 'from-pink-50 to-orange-50 dark:from-pink-900/20 dark:to-orange-900/20',
//               borderColor: 'border-pink-200 dark:border-pink-700',
//             },
//           ].map((feature, index) => (
//             <div
//               key={index}
//               className={`group animate-slide-up bg-gradient-to-br ${feature.bgGradient} rounded-2xl p-8 border ${feature.borderColor} hover:shadow-2xl hover:scale-105 transition-all duration-300`}
//               style={{ animationDelay: `${index * 100}ms` }}
//             >
//               <div className={`w-14 h-14 bg-gradient-to-r ${feature.gradient} rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
//                 <feature.icon className="w-7 h-7 text-white" />
//               </div>
//               <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
//                 {feature.title}
//               </h3>
//               <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
//                 {feature.description}
//               </p>
//             </div>
//           ))}
//         </div>

//         <div className="text-center animate-slide-up py-12">
//           <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
//             Ready to transform your documents?
//           </h2>
//           <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
//             Start using MRAG today and unlock the power of your documents
//           </p>
//           <button
//             onClick={onGetStarted}
//             className="group px-10 py-5 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 text-white rounded-2xl font-bold text-xl shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all duration-300 flex items-center gap-3 mx-auto"
//           >
//             Start For Free
//             <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform" />
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// }

import { ArrowRight, Sparkles, Zap, Shield, FileText } from 'lucide-react';
// Assuming useTheme and ThemeToggle are still required for the component logic
import { useTheme } from '../contexts/ThemeContext'; 
import { ThemeToggle } from './ThemeToggle';

interface HomepageProps {
  onGetStarted: () => void;
}

export function Homepage({ onGetStarted }: HomepageProps) {
  // useTheme is still available; we only need the toggle component here.
  useTheme();

  return (
    // Set background to neon-black and apply the overflow-x fix from original CSS
    <div className="min-h-screen bg-neon-black text-white overflow-hidden">
      
      {/* BACKGROUND GLOWS: Adjusted to Green/Cyan/Blue */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-50">
        {/* Subtle Green Glow */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-neon-green/30 rounded-full blur-3xl animate-float" />
        {/* Subtle Blue Core Glow (from data-flow-viz) */}
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-blue-500/30 rounded-full blur-3xl animate-float-delayed" />
        {/* New Cyan/Teal Glow */}
        <div className="absolute bottom-1/4 left-1/3 w-96 h-96 bg-cyan-500/30 rounded-full blur-3xl animate-float-slow" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-16 animate-slide-up relative">
          
          {/* Theme Toggle (kept for functionality, styled by its own component) */}
          <div className="absolute top-0 right-0 mt-6 mr-6 z-20">
            <ThemeToggle />
          </div>
          
          {/* Tagline: Styled to use neon-green */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-card-surface/50 rounded-full border border-neon-green/30 shadow-neon-light mb-6">
            <Sparkles className="w-4 h-4 text-neon-green neon-text-glow" />
            <span className="text-sm font-medium text-gray-300">
              Powered by AI & Vector Search
            </span>
          </div>

          {/* Headline: Applied the custom gradient/glow classes */}
          <h1 className="text-6xl md:text-7xl font-extrabold mb-6 leading-tight">
            <span className="app-title-gradient">
              MULTI-MODAL
            </span>
            <br />
            <span className="text-white neon-text-glow tracking-wide">
              RAG SYSTEM
            </span>
          </h1>

          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-12 leading-relaxed border-l-4 border-neon-green pl-4">
            Execute complex, multimodal queries grounded in diverse proprietary data sources (Text, Image, Audio, Video). Get accurate answers with context from your documents in seconds.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            {/* Primary Button: Neon Green Style */}
            <button
              onClick={onGetStarted}
              className="group px-8 py-4 bg-neon-green hover:bg-white text-neon-black rounded-2xl font-bold text-lg shadow-lg hover:shadow-neon-light transform hover:scale-105 transition-all duration-300 flex items-center gap-2"
            >
              Access System
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            
            {/* Secondary Button: Metallic Card Style */}
            <button
              onClick={() => {
                document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="px-8 py-4 metallic-card text-gray-300 rounded-2xl font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 border border-gray-700 hover:border-neon-green"
            >
              Learn More
            </button>
          </div>
        </div>

        {/* System Preview / Data Flow Visualization Section */}
        <div className="relative max-w-5xl mx-auto mb-20 animate-slide-up-delayed">
          {/* Replaced the colorful glow with the clean neon-light shadow */}
          <div className="absolute inset-0 shadow-neon-light rounded-3xl opacity-50" />
          
          {/* Applied metallic-card to the main preview container */}
          <div className="relative metallic-card rounded-3xl shadow-2xl border border-[#3A3A3A] overflow-hidden">
            
            {/* Header Bar: Neon Green Accent */}
            <div className="bg-card-highlight border-b border-[#3A3A3A] p-4 flex items-center gap-2">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-600" />
                <div className="w-3 h-3 rounded-full bg-yellow-600" />
                <div className="w-3 h-3 rounded-full bg-neon-green/80 shadow-lg shadow-neon-green" />
              </div>
              <span className="text-neon-green text-sm font-bold ml-4 neon-text-glow">
                RAG-X: Live Data Feed
              </span>
            </div>
            
            <div className="p-8 grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                {/* Feature Card 1: Metallic Card Style */}
                <div className="metallic-card rounded-2xl p-6 border border-neon-green/40">
                  <FileText className="w-8 h-8 text-neon-green neon-text-glow mb-3" />
                  <h3 className="font-semibold text-white mb-2">
                    Upload Documents
                  </h3>
                  <p className="text-sm text-gray-400">
                    Drag and drop your PDF, DOCX, or JSON files
                  </p>
                </div>
                {/* Feature Card 2: Metallic Card Style */}
                <div className="metallic-card rounded-2xl p-6 border border-blue-400/40"> 
                  <Zap className="w-8 h-8 text-blue-400 neon-text-glow mb-3" />
                  <h3 className="font-semibold text-white mb-2">
                    Ask Questions
                  </h3>
                  <p className="text-sm text-gray-400">
                    Get instant, grounded AI-powered answers
                  </p>
                </div>
              </div>
              
              {/* Visualization Placeholder: Applied data-flow-viz class */}
              <div className="data-flow-viz rounded-2xl p-6 flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-600/30 rounded-2xl mx-auto mb-4 flex items-center justify-center animate-pulse border border-blue-400/50">
                    <Sparkles className="w-8 h-8 text-blue-400 neon-text-glow" />
                  </div>
                  <p className="text-sm font-bold text-neon-green neon-text-glow">
                    VECTOR PROCESSING ONLINE
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Grid: Applied Metallic Card Style to all feature boxes */}
        <div id="features" className="grid md:grid-cols-3 gap-8 mb-20">
          {[
            {
              icon: Zap,
              title: 'Lightning Fast',
              description: 'Get instant responses powered by advanced vector search and AI models',
              iconColor: 'text-neon-green',
              borderColor: 'border-neon-green/30'
            },
            {
              icon: Shield,
              title: 'Secure & Private',
              description: 'Your documents are processed securely with enterprise-grade encryption',
              iconColor: 'text-blue-400',
              borderColor: 'border-blue-400/30'
            },
            {
              icon: Sparkles,
              title: 'Context-Aware',
              description: 'Retrieves relevant context from your documents for accurate answers',
              iconColor: 'text-cyan-400', // Replaced Pink with Cyan
              borderColor: 'border-cyan-400/30'
            },
          ].map((feature, index) => (
            <div
              key={index}
              className={`metallic-card group animate-slide-up rounded-2xl p-8 border ${feature.borderColor} hover:shadow-neon-light hover:scale-105 transition-all duration-300`}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {/* Icon Container: Darker background with icon glow */}
              <div className={`w-14 h-14 bg-card-surface border ${feature.borderColor} rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg shadow-neon-green/10`}>
                <feature.icon className={`w-7 h-7 ${feature.iconColor} neon-text-glow`} />
              </div>
              <h3 className="text-xl font-bold text-white mb-3 neon-text-glow">
                {feature.title}
              </h3>
              <p className="text-gray-400 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* CTA Section: Simplified for Neon/Metallic look */}
        <div className="text-center animate-slide-up py-12 border-t border-gray-700">
          <h2 className="text-4xl font-bold text-white mb-4 neon-text-glow">
            Ready to interface with the Matrix?
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Start using RAG-X today and unlock the intelligence in your data.
          </p>
          <button
            onClick={onGetStarted}
            className="group px-10 py-5 bg-neon-green hover:bg-white text-neon-black rounded-2xl font-bold text-xl shadow-lg hover:shadow-neon-light transform hover:scale-105 transition-all duration-300 flex items-center gap-3 mx-auto"
          >
            Initiate Query
            <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform" />
          </button>
        </div>
        
      </div>
    </div>
  );
}