#!/usr/bin/env python3
"""
LatticeReAct Interactive Terminal Chat Interface
=============================================
Terminal-based chatbot for materials science queries using the LatticeReAct framework.
"""

import sys
import os
import subprocess
import signal
import time
import threading
from datetime import datetime
import json

# Terminal colors and formatting
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class LatticeReActChat:
    def __init__(self):
        self.container_name = "latticereact-chat"
        self.container_running = False
        self.chat_history = []
        
    def print_banner(self):
        """Print the welcome banner"""
        print(f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                    🧪 LatticeReAct Chat 🧪                   ║
║            Interactive Materials Science Assistant            ║
║                                                              ║
║  Ask questions about materials properties, compositions,     ║
║  bandgaps, elastic properties, and thermodynamic data!      ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
{Colors.YELLOW}⚡ Powered by Multi-Agent Framework + Ollama + Materials Project{Colors.END}
{Colors.GREEN}🔬 Ready to analyze materials from quantum to bulk properties{Colors.END}
""")

    def check_dependencies(self):
        """Check if Docker and required services are available"""
        print(f"{Colors.BLUE}🔍 Checking system dependencies...{Colors.END}")
        
        # Check Docker
        try:
            subprocess.run(["docker", "--version"], 
                         capture_output=True, check=True)
            print(f"{Colors.GREEN}✅ Docker: Available{Colors.END}")
        except subprocess.CalledProcessError:
            print(f"{Colors.RED}❌ Docker not found. Please install Docker.{Colors.END}")
            return False
            
        # Check Ollama
        try:
            import requests
            resp = requests.get("http://localhost:11434/api/version", timeout=5)
            if resp.status_code == 200:
                version = resp.json().get('version', 'unknown')
                print(f"{Colors.GREEN}✅ Ollama: Running (v{version}){Colors.END}")
            else:
                raise Exception("Ollama not responding")
        except:
            print(f"{Colors.RED}❌ Ollama not running. Please start: ollama serve{Colors.END}")
            return False
            
        # Check if LatticeReAct image exists
        try:
            result = subprocess.run(["docker", "images", "-q", "latticereact-app"], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                print(f"{Colors.GREEN}✅ LatticeReAct Docker Image: Ready{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  Building LatticeReAct Docker image...{Colors.END}")
                self.build_image()
        except:
            print(f"{Colors.RED}❌ Failed to check Docker image{Colors.END}")
            return False
            
        return True
        
    def build_image(self):
        """Build the Docker image if needed"""
        print(f"{Colors.BLUE}🔨 Building LatticeReAct Docker image...{Colors.END}")
        try:
            result = subprocess.run(["docker", "build", "-t", "latticereact-app", "."], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Image built successfully{Colors.END}")
            else:
                print(f"{Colors.RED}❌ Build failed: {result.stderr[:200]}{Colors.END}")
                return False
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}❌ Build timeout (5 minutes){Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}❌ Build error: {e}{Colors.END}")
            return False
        return True

    def start_container(self):
        """Start the LatticeReAct container in background"""
        print(f"{Colors.BLUE}🚀 Starting LatticeReAct container...{Colors.END}")
        
        # Stop any existing container
        subprocess.run(["docker", "rm", "-f", self.container_name], 
                      capture_output=True)
        
        # Start new container
        cmd = [
            "docker", "run", "-d", "--name", self.container_name,
            "--env-file", ".env", "--network=host",
            "latticereact-app", "tail", "-f", "/dev/null"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.container_running = True
            print(f"{Colors.GREEN}✅ Container started: {result.stdout[:12]}{Colors.END}")
            
            # Wait a moment for container to be ready
            time.sleep(2)
            
            # Test container
            test_result = subprocess.run([
                "docker", "exec", self.container_name, 
                "python", "-c", "print('Container ready!')"
            ], capture_output=True, text=True)
            
            if test_result.returncode == 0:
                print(f"{Colors.GREEN}✅ Container is responsive{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Container not responding{Colors.END}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Failed to start container: {e.stderr}{Colors.END}")
            return False

    def query_supervisor(self, question):
        """Send query to LatticeReAct supervisor"""
        if not self.container_running:
            return "❌ Container not running. Please restart the chat."
            
        cmd = [
            "docker", "exec", self.container_name,
            "python", "run_supervisor.py", "--quiet", question
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                return result.stdout
            else:
                return f"❌ Query failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "⏱️ Query timeout (3 minutes). Try a simpler question."
        except Exception as e:
            return f"❌ Error: {e}"

    def show_typing_animation(self, stop_event):
        """Show typing animation while processing"""
        animation = ["🧪 ", "⚗️ ", "🔬 ", "📊 "]
        i = 0
        while not stop_event.is_set():
            print(f"\r{Colors.YELLOW}{animation[i % len(animation)]} Analyzing materials data...{Colors.END}", end="", flush=True)
            i += 1
            time.sleep(0.5)
        print(f"\r{' ' * 40}\r", end="")  # Clear line

    def format_response(self, response):
        """Format the response for better readability"""
        lines = response.split('\n')
        formatted = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('='):
                formatted.append(f"{Colors.CYAN}{line}{Colors.END}")
            elif line.startswith('FINAL ANSWER'):
                formatted.append(f"{Colors.GREEN}{Colors.BOLD}{line}{Colors.END}")
            elif line.startswith('Completed in'):
                formatted.append(f"{Colors.BLUE}{line}{Colors.END}")
            elif 'mp-' in line:
                formatted.append(f"{Colors.YELLOW}{line}{Colors.END}")
            else:
                formatted.append(line)
                
        return '\n'.join(formatted)

    def save_chat_history(self):
        """Save chat history to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.chat_history, f, indent=2, ensure_ascii=False)
            
        print(f"{Colors.BLUE}💾 Chat saved to: {filename}{Colors.END}")

    def show_help(self):
        """Show help information"""
        help_text = f"""
{Colors.CYAN}{Colors.BOLD}🛠️  LatticeReAct Chat Commands:{Colors.END}

{Colors.GREEN}Materials Queries:{Colors.END}
  • "What is the bandgap of Silicon?"
  • "What are the elastic properties of Iron?"
  • "Tell me about the thermal properties of Copper"
  • "What is the formation energy of NaCl?"
  
{Colors.GREEN}Special Commands:{Colors.END}
  • {Colors.BOLD}/help{Colors.END} or {Colors.BOLD}help{Colors.END} - Show this help
  • {Colors.BOLD}/history{Colors.END} - Show recent queries  
  • {Colors.BOLD}/save{Colors.END} - Save chat history to file
  • {Colors.BOLD}/clear{Colors.END} - Clear screen
  • {Colors.BOLD}/status{Colors.END} - Check system status
  • {Colors.BOLD}/exit{Colors.END} or {Colors.BOLD}quit{Colors.END} - Exit chat

{Colors.YELLOW}💡 Tips:{Colors.END}
  • Be specific about the material (use chemical formulas when possible)
  • Ask about specific properties (bandgap, bulk modulus, formation energy)
  • The system searches Materials Project database
  • Queries typically take 15-30 seconds
"""
        print(help_text)

    def show_status(self):
        """Show system status"""
        print(f"\n{Colors.CYAN}📊 System Status:{Colors.END}")
        
        # Container status
        if self.container_running:
            print(f"{Colors.GREEN}🐳 Docker Container: Running{Colors.END}")
        else:
            print(f"{Colors.RED}🐳 Docker Container: Stopped{Colors.END}")
            
        # Ollama status
        try:
            import requests
            resp = requests.get("http://localhost:11434/api/version", timeout=3)
            print(f"{Colors.GREEN}🧠 Ollama: Running (v{resp.json()['version']}){Colors.END}")
        except:
            print(f"{Colors.RED}🧠 Ollama: Not responding{Colors.END}")
            
        # Chat stats
        print(f"{Colors.BLUE}💬 Queries this session: {len(self.chat_history)}{Colors.END}")

    def show_history(self):
        """Show recent chat history"""
        if not self.chat_history:
            print(f"{Colors.YELLOW}📝 No queries in this session yet.{Colors.END}")
            return
            
        print(f"\n{Colors.CYAN}📜 Recent Queries:{Colors.END}")
        for i, entry in enumerate(self.chat_history[-5:], 1):
            timestamp = entry['timestamp']
            question = entry['question'][:50] + "..." if len(entry['question']) > 50 else entry['question']
            print(f"{Colors.BLUE}{i}. [{timestamp}]{Colors.END} {question}")

    def cleanup(self):
        """Cleanup resources"""
        print(f"\n{Colors.BLUE}🧹 Cleaning up...{Colors.END}")
        if self.container_running:
            subprocess.run(["docker", "rm", "-f", self.container_name], 
                          capture_output=True)
            print(f"{Colors.GREEN}✅ Container stopped{Colors.END}")

    def run(self):
        """Main chat loop"""
        try:
            self.print_banner()
            
            # Check dependencies
            if not self.check_dependencies():
                return 1
                
            # Start container
            if not self.start_container():
                return 1
                
            print(f"\n{Colors.GREEN}🎉 LatticeReAct Chat is ready!{Colors.END}")
            print(f"{Colors.BLUE}💡 Type 'help' for commands, or ask any materials question{Colors.END}")
            print(f"{Colors.BLUE}🚪 Type 'exit' or Ctrl+C to quit{Colors.END}\n")
            
            # Main chat loop
            while True:
                try:
                    # Get user input
                    question = input(f"{Colors.BOLD}🔬 You: {Colors.END}").strip()
                    
                    if not question:
                        continue
                        
                    # Handle special commands
                    if question.lower() in ['exit', 'quit', '/exit']:
                        break
                    elif question.lower() in ['help', '/help']:
                        self.show_help()
                        continue
                    elif question.lower() == '/history':
                        self.show_history()
                        continue
                    elif question.lower() == '/save':
                        self.save_chat_history()
                        continue
                    elif question.lower() == '/clear':
                        os.system('clear' if os.name == 'posix' else 'cls')
                        self.print_banner()
                        continue
                    elif question.lower() == '/status':
                        self.show_status()
                        continue
                        
                    # Process materials query
                    print(f"{Colors.CYAN}🤖 LatticeReAct: {Colors.END}", end="", flush=True)
                    
                    # Show typing animation
                    stop_animation = threading.Event()
                    animation_thread = threading.Thread(target=self.show_typing_animation, args=(stop_animation,))
                    animation_thread.start()
                    
                    # Query the supervisor
                    start_time = time.time()
                    response = self.query_supervisor(question)
                    end_time = time.time()
                    
                    # Stop animation
                    stop_animation.set()
                    animation_thread.join()
                    
                    # Format and display response
                    formatted_response = self.format_response(response)
                    print(f"{Colors.CYAN}🤖 LatticeReAct:{Colors.END}\n{formatted_response}\n")
                    
                    # Save to history
                    self.chat_history.append({
                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                        'question': question,
                        'response': response,
                        'duration': f"{end_time - start_time:.1f}s"
                    })
                    
                except KeyboardInterrupt:
                    print(f"\n{Colors.YELLOW}⚠️  Interrupting current query...{Colors.END}")
                    continue
                    
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}👋 Goodbye! Thanks for using LatticeReAct Chat{Colors.END}")
        except Exception as e:
            print(f"\n{Colors.RED}💥 Unexpected error: {e}{Colors.END}")
            return 1
        finally:
            self.cleanup()
            
        return 0

def main():
    """Entry point"""
    chat = LatticeReActChat()
    return chat.run()

if __name__ == "__main__":
    sys.exit(main())