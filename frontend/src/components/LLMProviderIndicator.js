import React, { useState, useEffect } from 'react';

const LLMProviderIndicator = () => {
  const [providerInfo, setProviderInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProviderInfo();
  }, []);

  const fetchProviderInfo = async () => {
    try {
      const response = await fetch('/api/v1/health');
      const data = await response.json();
      setProviderInfo({
        current: data.llm_provider || 'unknown',
        mistralAvailable: data.mistral_available || false,
        status: data.status || 'unknown'
      });
    } catch (error) {
      console.error('Failed to fetch provider info:', error);
      setProviderInfo({
        current: 'unknown',
        mistralAvailable: false,
        status: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const getProviderDisplay = (provider) => {
    const providers = {
      'mistral': {
        name: 'Mistral AI',
        icon: '🤖',
        color: 'text-blue-600',
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200'
      },
      'ollama': {
        name: 'Ollama',
        icon: '🦙',
        color: 'text-green-600',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200'
      },
      'auto': {
        name: 'Auto',
        icon: '⚡',
        color: 'text-purple-600',
        bgColor: 'bg-purple-50',
        borderColor: 'border-purple-200'
      },
      'unknown': {
        name: 'Unknown',
        icon: '❓',
        color: 'text-gray-600',
        bgColor: 'bg-gray-50',
        borderColor: 'border-gray-200'
      }
    };

    return providers[provider] || providers['unknown'];
  };

  if (loading) {
    return (
      <div className="flex items-center space-x-2 text-xs text-gray-500">
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
        <span>Checking AI provider...</span>
      </div>
    );
  }

  const provider = getProviderDisplay(providerInfo?.current);

  return (
    <div className="flex items-center space-x-2">
      <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${provider.bgColor} ${provider.color} ${provider.borderColor} border`}>
        <span className="mr-1">{provider.icon}</span>
        <span>Powered by {provider.name}</span>
      </div>
      
      {providerInfo?.mistralAvailable && (
        <div className="text-xs text-gray-500">
          <span className="inline-flex items-center">
            <div className="w-1.5 h-1.5 bg-green-400 rounded-full mr-1"></div>
            Mistral Ready
          </span>
        </div>
      )}
    </div>
  );
};

export default LLMProviderIndicator;
