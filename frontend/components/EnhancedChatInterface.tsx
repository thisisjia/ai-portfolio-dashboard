/**
 * Enhanced Chat Interface Component
 * Demonstrates modern React patterns, TypeScript, and component composition
 * Based on production experience with financial chat interfaces
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import { useSSEChat, ChatMessage } from '@/hooks/useSSEChat';
import { TokenAuthResponse } from '@/lib/api';
import MarkdownRenderer from './MarkdownRenderer';

interface ChatInterfaceProps {
  authData: TokenAuthResponse;
}

export default function EnhancedChatInterface({ authData }: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const {
    messages,
    currentResponse,
    isStreaming,
    error,
    currentAgent,
    statusMessage,
    sendMessage,
    clearMessages
  } = useSSEChat();

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentResponse, statusMessage]);

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;
    if (!authData.token || !authData.company) return;

    const messageText = input;
    setInput('');

    await sendMessage(
      messageText,
      authData.token,
      authData.company
    );

    // Focus back on input
    inputRef.current?.focus();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-900 to-slate-800">
      {/* Header */}
      <div className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white">
              Resume AI Assistant
            </h2>
            <p className="text-sm text-slate-400">
              Ask me anything about my experience and skills
            </p>
          </div>
          {currentAgent && (
            <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/20 rounded-full border border-blue-500/30">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
              <span className="text-sm text-blue-300 capitalize">
                {currentAgent} Agent
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !currentResponse && (
          <WelcomeScreen setInput={setInput} />
        )}

        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}

        {/* Status/Reasoning Display */}
        {isStreaming && statusMessage && (
          <div className="flex gap-3 items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
                <span className="text-white text-sm">⚡</span>
              </div>
            </div>
            <div className="flex-1">
              <div className="bg-amber-500/10 backdrop-blur-sm border border-amber-500/30 rounded-2xl rounded-tl-none px-4 py-2 shadow-lg">
                <p className="text-amber-300 text-sm font-medium flex items-center gap-2">
                  <span className="inline-block w-2 h-2 bg-amber-400 rounded-full animate-pulse" />
                  {statusMessage}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Streaming response */}
        {isStreaming && currentResponse && (
          <div className="flex gap-3">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-white text-sm">🤖</span>
              </div>
            </div>
            <div className="flex-1">
              <div className="bg-slate-800/80 backdrop-blur-sm rounded-2xl rounded-tl-none p-4 shadow-lg">
                <div>
                  <MarkdownRenderer content={currentResponse} className="text-sm" isDark={true} />
                  <span className="inline-block w-1 h-4 ml-1 bg-blue-400 animate-pulse" />
                </div>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-slate-800/50 backdrop-blur-sm border-t border-slate-700 p-4">
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isStreaming}
              placeholder="Ask me about my experience, skills, projects..."
              className="w-full bg-slate-900/50 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || isStreaming}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium rounded-xl hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-blue-500/20"
          >
            {isStreaming ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Thinking...
              </span>
            ) : (
              'Send'
            )}
          </button>
        </div>

        {/* Suggested questions */}
        {messages.length === 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {SUGGESTED_QUESTIONS.slice(0, 3).map((q, i) => (
              <button
                key={i}
                onClick={() => setInput(q)}
                className="text-xs px-3 py-1.5 bg-slate-700/50 hover:bg-slate-700 text-slate-300 rounded-full transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className="flex-shrink-0">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          isUser
            ? 'bg-gradient-to-br from-emerald-500 to-teal-600'
            : 'bg-gradient-to-br from-blue-500 to-purple-600'
        }`}>
          <span className="text-white text-sm">{isUser ? '👤' : '🤖'}</span>
        </div>
      </div>
      <div className="flex-1">
        <div className={`rounded-2xl p-4 shadow-lg ${
          isUser
            ? 'bg-gradient-to-br from-emerald-600 to-teal-700 rounded-tr-none ml-auto max-w-[80%]'
            : 'bg-slate-800/80 backdrop-blur-sm rounded-tl-none'
        }`}>
          <MarkdownRenderer content={message.content} className="text-sm" isDark={true} />
          {message.agent && (
            <p className="text-xs text-slate-400 mt-2 capitalize">
              via {message.agent} agent
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function WelcomeScreen({ setInput }: { setInput: (q: string) => void }) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center p-8">
      <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-6 shadow-lg shadow-blue-500/30">
        <span className="text-4xl">🤖</span>
      </div>
      <h3 className="text-2xl font-bold text-white mb-2">
        Welcome to My Interactive Resume
      </h3>
      <p className="text-slate-400 mb-8 max-w-md">
        I'm a multi-agent AI chatbot built with LangGraph and React.
        Ask me anything about my experience, skills, or projects!
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl">
        {SUGGESTED_QUESTIONS.map((q, i) => (
          <button
            key={i}
            onClick={() => setInput(q)}
            className="text-left p-4 bg-slate-800/50 border border-slate-700 rounded-lg hover:border-blue-500/50 hover:bg-slate-800 transition-all cursor-pointer"
          >
            <p className="text-sm text-slate-300">{q}</p>
          </button>
        ))}
      </div>
    </div>
  );
}

const SUGGESTED_QUESTIONS = [
  "What's your experience with React and TypeScript?",
  "Tell me about your LangGraph multi-agent systems",
  "What financial dashboards have you built?",
  "Explain your RAG implementation experience",
  "What's your work style and strengths?",
  "Tell me about your most impactful project"
];
