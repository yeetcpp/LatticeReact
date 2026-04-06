import { useState } from 'react';
import type { Message, ChatbotResponse } from '../types/chat';

const BACKEND_URL = 'http://localhost:8000';

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Welcome to LatticeReAct! I can help you explore materials properties across electronic, elastic, and thermodynamic domains. Ask me about any material!',
      isUser: false,
      timestamp: new Date(),
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      isUser: true,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: text.trim() }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data: ChatbotResponse = await response.json();
      
      // Clean the answer (remove agent internals)
      const cleanAnswer = cleanBotResponse(data.answer);
      
      // Add bot response
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: `${cleanAnswer}\n\n${data.source === 'cache' ? '📦 Retrieved from cache' : '🔍 Computed from live API'}`,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: '❌ Sorry, I encountered an error. Please make sure the backend server is running on port 8000.',
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearMessages = () => {
    setMessages([
      {
        id: '1',
        text: 'Welcome to LatticeReAct! I can help you explore materials properties across electronic, elastic, and thermodynamic domains. Ask me about any material!',
        isUser: false,
        timestamp: new Date(),
      }
    ]);
  };

  return {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
  };
};

// Clean agent internals from bot responses
const cleanBotResponse = (text: string): string => {
  const lines = text.split('\n');
  const cleaned = [];
  
  const skipPatterns = [
    '[THERMO_AGENT]',
    '[ELASTIC_AGENT]', 
    '[ELECTRONIC_AGENT]',
    'RESULTS FROM MATERIALS PROJECT DATABASE',
    'Direct Tool Output',
    '================',
    '= RESULTS',
    'Query: Give me',
    'Query: What',
    'Calling: ',
    'Please allow me',
    'Let me call',
    'I need to call',
    'tool result',
    'No interpretation',
    'No hallucination',
    'raw data directly',
    'IMPORTANT:',
  ];
  
  for (const line of lines) {
    const shouldSkip = skipPatterns.some(pattern => line.includes(pattern));
    if (!shouldSkip) {
      cleaned.push(line);
    }
  }
  
  let result = cleaned.join('\n').trim();
  
  // Remove multiple consecutive blank lines
  while (result.includes('\n\n\n')) {
    result = result.replace(/\n\n\n/g, '\n\n');
  }
  
  return result;
};