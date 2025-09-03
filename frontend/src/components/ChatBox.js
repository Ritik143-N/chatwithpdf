import React, { useState, useRef, useEffect, useCallback } from 'react';
import { askQuestionInSession, switchLLMProvider, getAvailableProviders, getSessionDetails } from '../services/api';
import ChatMessage from './ChatMessage';
import LLMProviderIndicator from './LLMProviderIndicator';
import ModelSelector from './ModelSelector';

const ChatBox = ({ uploadedDocument, currentSessionId, sessionData }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('gemini'); // Default to Gemini
  const [modelSwitching, setModelSwitching] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  // Memoize loadSessionMessages to avoid recreating it on every render
  const loadSessionMessages = useCallback(async () => {
    try {
      if (!currentSessionId) return;
      
      const sessionDetails = await getSessionDetails(currentSessionId);
      const sessionMessages = sessionDetails.messages || [];
      
      // Convert session messages to ChatBox format
      const formattedMessages = sessionMessages.map(msg => ({
        type: msg.message_type === 'user' ? 'user' : 'bot',
        content: msg.content,
        timestamp: new Date(msg.created_at),
        model: msg.model_used,
        context: msg.context_sources || []
      }));
      
      setMessages(formattedMessages);
    } catch (error) {
      console.error('Error loading session messages:', error);
      setMessages([]);
    }
  }, [currentSessionId]);

  // Load session messages when session changes
  useEffect(() => {
    if (currentSessionId && sessionData) {
      loadSessionMessages();
    } else {
      setMessages([]);
    }
  }, [currentSessionId, sessionData, loadSessionMessages]);

  // Initialize with current provider from backend
  useEffect(() => {
    const initializeProvider = async () => {
      try {
        const providers = await getAvailableProviders();
        if (providers && providers.current_provider) {
          setSelectedModel(providers.current_provider);
        }
      } catch (error) {
        console.error('Error fetching current provider:', error);
        // Keep default 'gemini' if error
      }
    };

    initializeProvider();
  }, []);

  const handleModelChange = async (modelId) => {
    if (modelId === selectedModel) return;

    setModelSwitching(true);
    try {
      const response = await switchLLMProvider(modelId);
      if (response.status === 'success') {
        setSelectedModel(modelId);
        
        // Add a system message about the model switch
        const systemMessage = {
          type: 'system',
          content: `Switched to ${modelId.charAt(0).toUpperCase() + modelId.slice(1)} model. You can continue the conversation with the new model.`,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, systemMessage]);
      } else {
        throw new Error(response.message || 'Failed to switch model');
      }
    } catch (error) {
      console.error('Error switching model:', error);
      
      // Add error message
      const errorMessage = {
        type: 'system',
        content: `Failed to switch to ${modelId} model. Please try again.`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setModelSwitching(false);
    }
  };

  // Add welcome message when document is uploaded
  useEffect(() => {
    if (uploadedDocument && messages.length === 0) {
      setMessages([{
        type: 'bot',
        content: 'Hi! I can help you with questions about your document. What would you like to know?',
        timestamp: new Date(),
      }]);
    }
  }, [uploadedDocument, messages.length]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    if (!uploadedDocument) {
      alert('Please upload a PDF document first');
      return;
    }

    if (!currentSessionId) {
      alert('No active session. Please upload a document to start a new session.');
      return;
    }

    const userMessage = {
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const question = inputValue.trim();
    setInputValue('');
    setLoading(true);

    try {
      // Use session-based messaging
      const response = await askQuestionInSession(currentSessionId, question);
      const botMessage = {
        type: 'bot',
        content: response.answer,
        context: response.context,
        timestamp: new Date(),
        model: selectedModel,
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        type: 'bot',
        content: 'Sorry, I encountered an error while processing your question. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Chat Header */}
      <div className="flex-shrink-0 border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h2 className="text-lg font-medium text-gray-900">Chat Assistant</h2>
            <p className="text-sm text-gray-500">
              {currentSessionId && sessionData 
                ? `Chatting about: ${sessionData.document_name || sessionData.document_filename || 'Document'}`
                : uploadedDocument 
                  ? 'Ask questions about your document' 
                  : 'Upload a document to start chatting'
              }
            </p>
            {currentSessionId && (
              <p className="text-xs text-blue-600 mt-1">
                Session: {currentSessionId.slice(0, 8)}...
              </p>
            )}
            <div className="mt-2">
              <LLMProviderIndicator />
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Model Selector */}
            <div className="flex flex-col items-end">
              <div className="mb-2">
                <ModelSelector 
                  selectedModel={selectedModel}
                  onModelChange={handleModelChange}
                />
              </div>
              {modelSwitching && (
                <div className="flex items-center space-x-2 text-xs text-blue-600">
                  <div className="w-3 h-3 border border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                  <span>Switching model...</span>
                </div>
              )}
            </div>
            
            {/* Status Indicator */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${currentSessionId ? 'bg-green-400' : uploadedDocument ? 'bg-yellow-400' : 'bg-gray-400'}`}></div>
              <span className="text-xs text-gray-500">
                {currentSessionId ? 'Active Session' : uploadedDocument ? 'Ready' : 'Waiting'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !uploadedDocument && (
          <div className="text-center text-gray-500 py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <p className="text-lg font-medium text-gray-900 mb-2">Ready to chat!</p>
            <p className="text-gray-500">Upload a PDF document to start asking questions about its content.</p>
          </div>
        )}

        {messages.map((message, index) => (
          <ChatMessage
            key={index}
            message={message.content}
            isUser={message.type === 'user'}
            isSystem={message.type === 'system'}
            isError={message.isError}
            timestamp={message.timestamp}
            onCopy={async (text) => {
              try {
                await navigator.clipboard.writeText(text);
                // Could add a toast notification here
              } catch (err) {
                console.error('Failed to copy text:', err);
              }
            }}
          />
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-2">
              <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 2a8 8 0 100 16 8 8 0 000-16zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                  <span className="text-sm">Thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 border-t border-gray-200 p-4">
        <form onSubmit={handleSendMessage} className="flex space-x-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={uploadedDocument ? "Ask a question about your document..." : "Upload a PDF to start chatting..."}
              disabled={!uploadedDocument || loading}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed pr-12"
            />
            <button
              type="submit"
              disabled={!uploadedDocument || loading || !inputValue.trim()}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 rounded-full text-purple-600 hover:bg-purple-50 disabled:text-gray-400 disabled:cursor-not-allowed disabled:hover:bg-transparent"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </form>
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
          <span>Press Enter to send</span>
          <span className="flex items-center">
            <div className="w-2 h-2 bg-green-400 rounded-full mr-1"></div>
            Local AI
          </span>
        </div>
      </div>
    </div>
  );
};

export default ChatBox;
