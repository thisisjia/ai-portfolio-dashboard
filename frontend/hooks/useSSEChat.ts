/**
 * SSE Chat Hook - Showcasing React Query patterns and TypeScript
 * Based on real production experience with investment intelligence platforms
 */

import { useState, useCallback, useRef } from 'react';

export interface ChatChunk {
  type: 'status' | 'agent_change' | 'token' | 'response' | 'done' | 'error';
  message?: string;
  agent?: string;
  content?: string;
  confidence?: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  agent?: string;
  timestamp: Date;
}

export interface UseSSEChatReturn {
  messages: ChatMessage[];
  currentResponse: string;
  isStreaming: boolean;
  error: string | null;
  currentAgent: string | null;
  statusMessage: string | null;
  sendMessage: (message: string, token: string, company: string, sessionId?: string) => Promise<void>;
  clearMessages: () => void;
}

/**
 * Custom hook for SSE-based chat streaming
 * Demonstrates modern React patterns used in production financial dashboards
 */
export function useSSEChat(): UseSSEChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentResponse, setCurrentResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (
    message: string,
    token: string,
    company: string,
    sessionId?: string
  ) => {
    // Add user message immediately
    const userMessage: ChatMessage = {
      role: 'user',
      content: message,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    setIsStreaming(true);
    setCurrentResponse('');
    setError(null);
    setCurrentAgent(null);
    setStatusMessage(null);

    // Create abort controller for request cancellation
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9001'}/api/chat/message/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          token,
          company,
          session_id: sessionId
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No reader available');
      }

      let buffer = '';
      let accumulatedResponse = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        // Decode chunk
        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE messages
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6); // Remove 'data: ' prefix

            try {
              const chunk: ChatChunk = JSON.parse(data);

              switch (chunk.type) {
                case 'status':
                  // Show status in UI
                  setStatusMessage(chunk.message || null);
                  console.log('📡 Status:', chunk.message);
                  break;

                case 'agent_change':
                  setCurrentAgent(chunk.agent || null);
                  setStatusMessage(`Routing to ${chunk.agent} agent...`);
                  console.log('🤖 Agent:', chunk.agent);
                  break;

                case 'token':
                  // Append token to current response (streaming effect)
                  accumulatedResponse += chunk.content || '';
                  setCurrentResponse(accumulatedResponse);
                  break;

                case 'response':
                  // Full response received
                  accumulatedResponse = chunk.content || '';
                  setCurrentResponse(accumulatedResponse);
                  setCurrentAgent(chunk.agent || null);
                  break;

                case 'done':
                  // Stream complete - add assistant message
                  const assistantMessage: ChatMessage = {
                    role: 'assistant',
                    content: accumulatedResponse,
                    agent: currentAgent || undefined,
                    timestamp: new Date()
                  };
                  setMessages(prev => [...prev, assistantMessage]);
                  setCurrentResponse('');
                  setIsStreaming(false);
                  setCurrentAgent(null);
                  setStatusMessage(null);
                  break;

                case 'error':
                  throw new Error(chunk.message || 'Unknown error');
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }
    } catch (err) {
      if (err instanceof Error) {
        if (err.name === 'AbortError') {
          console.log('Request cancelled');
        } else {
          setError(err.message);
        }
      } else {
        setError('Unknown error occurred');
      }
      setIsStreaming(false);
      setCurrentAgent(null);
      setStatusMessage(null);
    } finally {
      abortControllerRef.current = null;
    }
  }, [currentAgent]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentResponse('');
    setError(null);
  }, []);

  return {
    messages,
    currentResponse,
    isStreaming,
    error,
    currentAgent,
    statusMessage,
    sendMessage,
    clearMessages
  };
}
