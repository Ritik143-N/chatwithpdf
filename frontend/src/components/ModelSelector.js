import React, { useState, useEffect } from 'react';

const ModelSelector = ({ selectedModel, onModelChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  const models = [
    {
      id: 'gemini',
      name: 'Google Gemini',
      description: 'Fast and intelligent responses',
      color: 'bg-blue-500',
      icon: '🧠'
    },
    {
      id: 'mistral',
      name: 'Mistral AI',
      description: 'High-quality language understanding',
      color: 'bg-purple-500',
      icon: '⚡'
    },
    {
      id: 'ollama',
      name: 'Ollama Local',
      description: 'Privacy-focused local processing',
      color: 'bg-green-500',
      icon: '🏠'
    }
  ];

  const currentModel = models.find(model => model.id === selectedModel) || models[0];

  const handleModelSelect = (modelId) => {
    onModelChange(modelId);
    setIsOpen(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isOpen && !event.target.closest('.model-selector')) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  return (
    <div className="model-selector relative">
      {/* Current Selection Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
      >
        <div className={`w-3 h-3 rounded-full ${currentModel.color}`}></div>
        <span className="text-sm font-medium text-gray-700">{currentModel.icon}</span>
        <span className="text-sm font-medium text-gray-900">{currentModel.name}</span>
        <svg
          className={`w-4 h-4 text-gray-500 transform transition-transform ${
            isOpen ? 'rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-full mt-2 w-72 bg-white border border-gray-200 rounded-lg shadow-lg z-50 overflow-hidden">
          <div className="py-2">
            {models.map((model) => (
              <button
                key={model.id}
                onClick={() => handleModelSelect(model.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 hover:bg-gray-50 transition-colors ${
                  model.id === selectedModel ? 'bg-blue-50 border-r-2 border-blue-500' : ''
                }`}
              >
                <div className={`w-4 h-4 rounded-full ${model.color} flex-shrink-0`}></div>
                <div className="flex-1 text-left">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{model.icon}</span>
                    <span className="font-medium text-gray-900">{model.name}</span>
                    {model.id === selectedModel && (
                      <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{model.description}</p>
                </div>
              </button>
            ))}
          </div>
          
          {/* Footer */}
          <div className="border-t border-gray-100 px-4 py-3 bg-gray-50">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">
                Switch models anytime during conversation
              </span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-xs text-green-600 font-medium">All models ready</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelSelector;
