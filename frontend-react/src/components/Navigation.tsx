interface NavigationProps {
  onEnterChat: () => void;
}

export const Navigation = ({ onEnterChat }: NavigationProps) => {
  return (
    <nav className="fixed top-0 w-full z-50 bg-[#1e1e2e]/40 backdrop-blur-xl shadow-[0_0_40px_rgba(173,198,255,0.06)]">
      <div className="flex justify-between items-center px-8 py-4 max-w-screen-2xl mx-auto">
        <div className="text-xl font-bold tracking-tighter text-[#adc6ff] font-space">
          LatticeReAct
        </div>
        <div className="hidden md:flex gap-8 items-center">
          <a className="text-[#4fdbc8] font-bold border-b border-[#4fdbc8] font-space text-sm tracking-tight transition-colors duration-300" href="#">
            Docs
          </a>
          <a className="text-[#adc6ff]/70 hover:text-[#cebdff] font-space text-sm tracking-tight transition-colors duration-300" href="#">
            Agents
          </a>
          <a className="text-[#adc6ff]/70 hover:text-[#cebdff] font-space text-sm tracking-tight transition-colors duration-300" href="#">
            Benchmarks
          </a>
          <button 
            onClick={onEnterChat}
            className="btn-primary"
          >
            Enter Chat
          </button>
        </div>
      </div>
    </nav>
  );
};