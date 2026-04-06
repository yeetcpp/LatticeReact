import { Navigation } from './components/Navigation';
import { HeroSection } from './components/HeroSection';
import { MetricsSection } from './components/MetricsSection';
import { ChatSection } from './components/ChatSection';
import { BenchmarksSection } from './components/BenchmarksSection';
import { Footer } from './components/Footer';
import './App.css';

function App() {
  const scrollToChat = () => {
    const chatElement = document.getElementById('chat-section');
    chatElement?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="bg-[#121221] text-[#e3e0f6] selection:bg-[#4fdbc8]/30">
      <Navigation onEnterChat={scrollToChat} />
      <HeroSection onEnterChat={scrollToChat} />
      <MetricsSection />
      <div id="chat-section">
        <ChatSection />
      </div>
      <BenchmarksSection />
      <Footer />
    </div>
  );
}

export default App;
