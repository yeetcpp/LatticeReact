export const MetricsSection = () => {
  return (
    <section className="py-24 relative bg-[#1a1a2a]">
      <div className="container mx-auto px-6">
        <div className="flex flex-col mb-16">
          <h2 className="font-headline text-3xl font-bold mb-2">Performance Metrics</h2>
          <div className="w-24 h-1 bg-[#4fdbc8] rounded-full"></div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-8">
          {/* Accuracy Metric */}
          <div className="surface-container p-8 rounded-lg spectral-glow relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-30 transition-opacity">
              <span className="material-symbols-outlined text-4xl">verified</span>
            </div>
            <div className="font-mono text-[#4fdbc8] text-xs mb-2">ACCURACY</div>
            <div className="font-headline text-5xl font-bold mb-1">100%</div>
            <div className="font-body text-xs text-[#c2c6d6] uppercase tracking-widest">Verified Baseline</div>
          </div>

          {/* Hallucination Rate */}
          <div className="surface-container p-8 rounded-lg spectral-glow relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-30 transition-opacity">
              <span className="material-symbols-outlined text-4xl">shield</span>
            </div>
            <div className="font-mono text-[#4fdbc8] text-xs mb-2">HALLUCINATION RATE</div>
            <div className="font-headline text-5xl font-bold mb-1">0%</div>
            <div className="font-body text-xs text-[#c2c6d6] uppercase tracking-widest">Zero-Noise Inference</div>
          </div>

          {/* Test Success */}
          <div className="surface-container p-8 rounded-lg spectral-glow relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-30 transition-opacity">
              <span className="material-symbols-outlined text-4xl">check_circle</span>
            </div>
            <div className="font-mono text-[#4fdbc8] text-xs mb-2">TEST SUCCESS</div>
            <div className="font-headline text-5xl font-bold mb-1">90%</div>
            <div className="font-body text-xs text-[#c2c6d6] uppercase tracking-widest">9/10 Validation Loops</div>
          </div>

          {/* Inference Speed */}
          <div className="surface-container p-8 rounded-lg spectral-glow relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-30 transition-opacity">
              <span className="material-symbols-outlined text-4xl">speed</span>
            </div>
            <div className="font-mono text-[#4fdbc8] text-xs mb-2">INFERENCE SPEED</div>
            <div className="font-headline text-5xl font-bold mb-1">22s</div>
            <div className="font-body text-xs text-[#c2c6d6] uppercase tracking-widest">Average Per Sequence</div>
          </div>
        </div>

        {/* Tech Stack Grid */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="surface-container p-10 rounded-lg border border-[#424754]/10 flex flex-col justify-between">
            <div>
              <h3 className="font-headline text-2xl font-bold mb-6 flex items-center gap-3">
                <span className="material-symbols-outlined text-[#adc6ff]">terminal</span>
                Infrastructure Stack
              </h3>
              <div className="grid grid-cols-2 gap-4">
                {['Qwen2.5 14B', 'ChromaDB', 'LangChain', 'Docker/Ollama'].map((tech, index) => (
                  <div key={index} className="flex items-center gap-3 bg-[#1a1a2a] p-3 rounded">
                    <span className="w-2 h-2 bg-[#adc6ff] rounded-full"></span>
                    <span className="font-mono text-sm">{tech}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="mt-8 flex items-center justify-between border-t border-[#424754]/10 pt-6">
              <div className="font-mono text-[10px] text-[#c2c6d6] uppercase tracking-widest">Deployment Strategy</div>
              <div className="text-[#4fdbc8] font-bold font-mono">LOCAL_HOST_ISOLATION</div>
            </div>
          </div>

          <div className="surface-container p-10 rounded-lg border border-[#424754]/10 bg-gradient-to-br from-[#1e1e2e] to-[#343344]">
            <h3 className="font-headline text-2xl font-bold mb-6 flex items-center gap-3">
              <span className="material-symbols-outlined text-[#4fdbc8]">database</span>
              Materials Repository
            </h3>
            <div className="flex items-baseline gap-4 mb-4">
              <span className="text-6xl font-headline font-bold">150K+</span>
              <span className="font-mono text-[#c2c6d6] text-sm">Compounds</span>
            </div>
            <p className="font-body text-[#c2c6d6] leading-relaxed">
              Direct integration with the Materials Project API, enabling real-time verification of lattice structures and thermodynamic stability across the known chemical space.
            </p>
            <div className="mt-12 flex gap-2">
              {[100, 85, 92].map((width, index) => (
                <div key={index} className="h-1 flex-grow bg-[#4fdbc8]/20 rounded-full overflow-hidden">
                  <div className="h-full bg-[#4fdbc8]" style={{width: `${width}%`}}></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};