export const Footer = () => {
  return (
    <footer className="bg-[#121221] w-full border-t border-[#adc6ff]/10">
      <div className="flex flex-col md:flex-row justify-between items-center px-12 py-8 w-full gap-6">
        <div className="font-mono text-[10px] uppercase tracking-widest text-[#adc6ff]/50">
          © 2024 LatticeReAct Labs
        </div>
        <div className="flex gap-8 items-center">
          <a className="font-mono text-[10px] uppercase tracking-widest text-[#adc6ff]/50 hover:text-[#4fdbc8] transition-opacity" href="#">
            Repository
          </a>
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-[#4fdbc8] rounded-full animate-pulse"></span>
            <span className="font-mono text-[10px] uppercase tracking-widest text-[#4fdbc8]">
              System Status: Operational
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};