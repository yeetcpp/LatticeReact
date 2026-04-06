export const BenchmarksSection = () => {
  return (
    <section className="py-24 bg-[#0d0d1c] relative overflow-hidden">
      <div className="absolute top-0 right-0 w-1/2 h-full bg-[#adc6ff]/5 blur-[120px] rounded-full pointer-events-none"></div>
      
      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center mb-20">
          <h2 className="font-headline text-4xl font-bold mb-6 tracking-tight">Benchmark Analysis</h2>
          <p className="font-body text-[#c2c6d6] max-w-2xl mx-auto">
            A direct comparison of chemical reasoning accuracy and hallucination frequency between generic LLMs and the LatticeReAct framework.
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Comparison Charts */}
          <div className="space-y-8">
            {/* Hallucination Rate */}
            <div className="glass p-6 rounded-lg border border-[#424754]/10">
              <div className="flex justify-between items-end mb-4">
                <span className="font-headline font-bold">Hallucination Rate</span>
                <span className="font-mono text-xs text-[#c2c6d6]">LOWER IS BETTER</span>
              </div>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-xs font-mono mb-1">
                    <span>ChatGPT (GPT-4o)</span>
                    <span>32%</span>
                  </div>
                  <div className="h-2 bg-[#1e1e2e] rounded-full overflow-hidden">
                    <div className="h-full bg-[#93000a] w-[32%]"></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs font-mono mb-1">
                    <span className="text-[#4fdbc8]">LatticeReAct</span>
                    <span className="text-[#4fdbc8]">0%</span>
                  </div>
                  <div className="h-2 bg-[#1e1e2e] rounded-full overflow-hidden">
                    <div className="h-full bg-[#4fdbc8] w-0 group-hover:w-full transition-all duration-1000"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Scientific Accuracy */}
            <div className="glass p-6 rounded-lg border border-[#424754]/10">
              <div className="flex justify-between items-end mb-4">
                <span className="font-headline font-bold">Scientific Accuracy</span>
                <span className="font-mono text-xs text-[#c2c6d6]">HIGHER IS BETTER</span>
              </div>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-xs font-mono mb-1">
                    <span>Standard RAG</span>
                    <span>74%</span>
                  </div>
                  <div className="h-2 bg-[#1e1e2e] rounded-full overflow-hidden">
                    <div className="h-full bg-[#4d8eff] w-[74%] opacity-50"></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs font-mono mb-1">
                    <span className="text-[#4fdbc8]">LatticeReAct (Verified)</span>
                    <span className="text-[#4fdbc8]">100%</span>
                  </div>
                  <div className="h-2 bg-[#1e1e2e] rounded-full overflow-hidden">
                    <div className="h-full bg-[#4fdbc8] w-full"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Lab Image & Caption */}
          <div className="relative group">
            <div className="absolute inset-0 bg-[#4fdbc8]/10 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <img 
              alt="Laboratory Visualization" 
              className="rounded-lg shadow-2xl relative z-10 border border-[#424754]/20" 
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuB5NJC1SaNBizUePtm_slit9H60jglKxSzL6O9PJjA6FYrvKJrKLKQyvZYT-RuISMQILE2gp7d-PnRUibRHbKqxVU3QRFnXbnrsxA-CZd2N41V0XAKfieFIoSgJi9dSSh4fieTWfO4TNvnw-rOdtmvXaMI641qdR0q9ItPqunP6m_grlj9xzImgx_Hft2two4i0yBxikfAL276dnj_Cv4u9IR3HHteak7tBLFBoqQk-cUbORAto-de80Hy6pNAEU1YDXemI5rk9-iQo" 
            />
            <div className="mt-8 p-6 glass rounded-lg border border-[#424754]/10 relative z-10">
              <h4 className="font-headline font-bold text-lg mb-2">Zero-Hallucination Protocol</h4>
              <p className="font-body text-sm text-[#c2c6d6] italic">
                "By implementing a recursive validation loop that cross-references all agentic outputs against the Materials Project ground truth, we eliminate the probabilistic errors inherent in autoregressive models."
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};