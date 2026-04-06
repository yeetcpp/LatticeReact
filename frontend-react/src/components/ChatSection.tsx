import { useState } from 'react';
import { useChat } from '../hooks/useChat';

export const ChatSection = () => {
  const { messages, isLoading, sendMessage } = useChat();
  const [input, setInput] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const message = input;
    setInput('');
    await sendMessage(message);
  };

  const quickQueries = [
    "Predict the stability and lattice parameters for BaZrO3",
    "What is the bandgap of GaN?",
    "Compare formation energies of TiO2, Al2O3, and SiO2",
    "Electronic properties of Silicon"
  ];

  return (
    <section className="py-24 bg-[#121221]">
      <div className="container mx-auto px-6">
        <div className="max-w-4xl mx-auto border border-[#424754]/20 rounded-xl overflow-hidden glass shadow-2xl">
          {/* Chat Header */}
          <div className="bg-[#292839] px-6 py-4 flex justify-between items-center border-b border-[#424754]/10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#adc6ff]/20 rounded-lg flex items-center justify-center">
                <span className="material-symbols-outlined text-[#adc6ff]" style={{fontVariationSettings: "'FILL' 1"}}>science</span>
              </div>
              <div>
                <h4 className="font-headline font-bold text-sm leading-none">LatticeReAct v1.0</h4>
                <span className="font-mono text-[10px] text-[#4fdbc8]">ACTIVE_INFERENCE</span>
              </div>
            </div>
            <div className="flex gap-4">
              <span className="material-symbols-outlined text-[#c2c6d6] text-sm">settings</span>
              <span className="material-symbols-outlined text-[#c2c6d6] text-sm">info</span>
            </div>
          </div>

          {/* Quick Queries */}
          <div className="p-4 border-b border-[#424754]/10">
            <p className="text-sm text-[#c2c6d6] mb-3">Quick Examples:</p>
            <div className="flex flex-wrap gap-2">
              {quickQueries.map((query, index) => (
                <button
                  key={index}
                  onClick={() => setInput(query)}
                  className="px-3 py-1 text-xs glass rounded-full hover:bg-white/20 transition-colors"
                >
                  {query.length > 40 ? query.substring(0, 40) + '...' : query}
                </button>
              ))}
            </div>
          </div>

          {/* Messages */}
          <div className="h-[500px] overflow-y-auto p-8 space-y-6 flex flex-col">
            {messages.map((message, index) => (
              <div 
                key={message.id} 
                className={`flex gap-4 max-w-[85%] ${message.isUser ? 'self-end flex-row-reverse' : ''}`}
              >
                <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${
                  message.isUser ? 'bg-[#4fdbc8]/20' : 'bg-[#adc6ff]/20'
                }`}>
                  <span className={`material-symbols-outlined text-xs ${
                    message.isUser ? 'text-[#4fdbc8]' : 'text-[#adc6ff]'
                  }`}>
                    {message.isUser ? 'person' : 'smart_toy'}
                  </span>
                </div>
                
                <div className={`p-4 rounded-lg border ${
                  message.isUser 
                    ? 'bg-[#343344] rounded-tr-none border-[#4fdbc8]/20' 
                    : 'bg-[#1e1e2e] rounded-tl-none border-[#424754]/10'
                }`}>
                  {!message.isUser && index > 0 && (
                    <div className="font-mono text-[10px] text-[#adc6ff] mb-2 uppercase tracking-tighter">
                      [REACT-AGENT: ANALYZING_MATERIALS]
                    </div>
                  )}
                  
                  <div className="font-body text-sm leading-relaxed whitespace-pre-wrap">
                    {message.text}
                  </div>
                  
                  {!message.isUser && index > 0 && (
                    <div className="mt-4 pt-4 border-t border-[#424754]/10 flex items-center gap-4">
                      <div className="flex items-center gap-1 text-[10px] font-mono text-[#4fdbc8]">
                        <span className="material-symbols-outlined text-[12px]">verified</span> 0% HALLUCINATION
                      </div>
                      <div className="flex items-center gap-1 text-[10px] font-mono text-[#c2c6d6]">
                        <span className="material-symbols-outlined text-[12px]">timer</span> 2.4s INFERENCE
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Typing Indicator */}
            {isLoading && (
              <div className="flex gap-4 items-center animate-pulse">
                <div className="w-8 h-8 rounded-full bg-[#adc6ff]/10 flex-shrink-0 flex items-center justify-center">
                  <span className="material-symbols-outlined text-[#adc6ff]/40 text-xs">smart_toy</span>
                </div>
                <div className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-[#adc6ff]/40 rounded-full"></span>
                  <span className="w-1.5 h-1.5 bg-[#adc6ff]/40 rounded-full"></span>
                  <span className="w-1.5 h-1.5 bg-[#adc6ff]/40 rounded-full"></span>
                </div>
              </div>
            )}
          </div>

          {/* Chat Input */}
          <div className="p-6 bg-[#1a1a2a] border-t border-[#424754]/10">
            <form onSubmit={handleSubmit} className="relative">
              <input 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="w-full bg-[#0d0d1c] border-none border-b-2 border-[#424754]/30 focus:border-[#4fdbc8] focus:ring-0 rounded-t-lg px-6 py-4 font-body text-sm text-[#e3e0f6] placeholder:text-[#c2c6d6]/40 transition-colors" 
                placeholder="Inquire about compound structures..." 
                type="text"
                disabled={isLoading}
              />
              <button 
                type="submit"
                disabled={!input.trim() || isLoading}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-[#4fdbc8] hover:text-[#cebdff] transition-colors disabled:opacity-50"
              >
                <span className="material-symbols-outlined">send</span>
              </button>
            </form>
            
            <div className="mt-3 flex gap-4">
              <button className="text-[10px] font-mono text-[#c2c6d6] hover:text-[#adc6ff] transition-colors flex items-center gap-1">
                <span className="material-symbols-outlined text-sm">attach_file</span> ATTACH_DATA
              </button>
              <button className="text-[10px] font-mono text-[#c2c6d6] hover:text-[#adc6ff] transition-colors flex items-center gap-1">
                <span className="material-symbols-outlined text-sm">history</span> PREV_QUERIES
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};