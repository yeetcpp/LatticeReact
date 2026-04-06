import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Loader2, RotateCcw, Sparkles, X } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import type { Message } from '../types/chat';

interface ChatInterfaceProps {
  isOpen: boolean;
  onClose: () => void;
}

const MessageBubble = ({ message, index }: { message: Message; index: number }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.8 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: index * 0.1, duration: 0.3 }}
      className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`max-w-[80%] ${message.isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            message.isUser
              ? 'bg-gradient-to-r from-accent-purple to-accent-teal text-white'
              : 'glass-morphism text-white'
          } shadow-lg`}
        >
          <div className="whitespace-pre-wrap text-sm leading-relaxed">
            {message.text}
          </div>
          <div className="text-xs opacity-70 mt-1">
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>
      </div>
      
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
        message.isUser ? 'order-1 mr-2 bg-accent-gold' : 'order-2 ml-2 bg-accent-purple'
      }`}>
        {message.isUser ? '👤' : '🔬'}
      </div>
    </motion.div>
  );
};

const TypingIndicator = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="flex justify-start mb-4"
    >
      <div className="flex items-center space-x-2 glass-morphism rounded-2xl px-4 py-3">
        <div className="flex space-x-1">
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
            className="w-2 h-2 bg-accent-purple rounded-full"
          />
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
            className="w-2 h-2 bg-accent-teal rounded-full"
          />
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
            className="w-2 h-2 bg-accent-blue rounded-full"
          />
        </div>
        <span className="text-xs text-gray-300">LatticeReAct is thinking...</span>
      </div>
    </motion.div>
  );
};

export const ChatInterface = ({ isOpen, onClose }: ChatInterfaceProps) => {
  const { messages, isLoading, sendMessage, clearMessages } = useChat();
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const message = inputValue;
    setInputValue('');
    await sendMessage(message);
  };

  const quickQueries = [
    "What is the bandgap of GaN?",
    "Bulk modulus of Iron",
    "Formation energy of NaCl",
    "Electronic properties of Silicon"
  ];

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
    >
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.8, opacity: 0 }}
        transition={{ type: 'spring', duration: 0.5 }}
        className="w-full max-w-4xl h-[90vh] glass-card flex flex-col overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/20">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-accent-purple to-accent-teal rounded-full flex items-center justify-center">
              <Sparkles size={20} />
            </div>
            <div>
              <h2 className="text-xl font-bold text-glow">LatticeReAct Chat</h2>
              <p className="text-sm text-gray-400">Materials Intelligence Assistant</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={clearMessages}
              className="btn-icon"
              title="Clear conversation"
            >
              <RotateCcw size={18} />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onClose}
              className="btn-icon"
            >
              <X size={18} />
            </motion.button>
          </div>
        </div>

        {/* Quick Query Buttons */}
        <div className="p-4 border-b border-white/10">
          <p className="text-sm text-gray-400 mb-3">Quick Examples:</p>
          <div className="flex flex-wrap gap-2">
            {quickQueries.map((query, index) => (
              <motion.button
                key={index}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setInputValue(query)}
                className="btn-ghost text-xs"
              >
                {query}
              </motion.button>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message, index) => (
            <MessageBubble key={message.id} message={message} index={index} />
          ))}
          
          <AnimatePresence>
            {isLoading && <TypingIndicator />}
          </AnimatePresence>
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-6 border-t border-white/20">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <div className="flex-1 relative">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask about materials properties..."
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-purple focus:border-transparent text-white placeholder-gray-400"
                disabled={isLoading}
              />
            </div>
            <motion.button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn-primary"
            >
              {isLoading ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Send size={18} />
              )}
              <span>Send</span>
            </motion.button>
          </form>
        </div>
      </motion.div>
    </motion.div>
  );
};