interface HeroSectionProps {
  onEnterChat: () => void;
}

export const HeroSection = ({ onEnterChat }: HeroSectionProps) => {
  return (
    <section className="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden hex-bg">
      {/* Decorative Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-32 h-32 opacity-20 border border-[#4d8eff] rounded-full animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-48 h-48 opacity-10 border border-[#4fdbc8] rounded-full animate-pulse" style={{animationDelay: '1s'}}></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-64 bg-gradient-to-b from-transparent via-[#adc6ff]/20 to-transparent rotate-45"></div>
      </div>

      <div className="container mx-auto px-6 relative z-10 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1 glass rounded-full border border-[#424754]/20 mb-8">
          <span className="w-2 h-2 rounded-full bg-[#4fdbc8]"></span>
          <span className="font-mono text-[10px] uppercase tracking-widest text-[#4fdbc8]">
            Zero-Hallucination Framework
          </span>
        </div>

        <h1 className="font-headline text-5xl md:text-7xl lg:text-8xl font-bold tracking-tighter mb-8 leading-tight">
          LatticeReAct: A <span className="gradient-text">Zero-Hallucination</span>{' '}
          <br />
          Agentic Framework
        </h1>

        <p className="font-body text-[#c2c6d6] max-w-3xl mx-auto text-lg md:text-xl mb-12 leading-relaxed">
          Transforming computational chemistry with high-fidelity, scientific editorial experiences. 
          Local execution for privacy, jury-grade reliability for materials science.
        </p>

        <div className="flex flex-col md:flex-row gap-6 justify-center items-center">
          <button 
            onClick={onEnterChat}
            className="btn-primary-lg"
          >
            Explore Chat
          </button>
          <button className="btn-secondary-lg">
            Technical Specs
          </button>
        </div>
      </div>

      <div className="absolute bottom-0 w-full h-32 bg-gradient-to-t from-[#121221] to-transparent"></div>
    </section>
  );
};