import React from 'react';

/**
 * MarkdownRenderer component to render markdown text with proper formatting
 * Handles common markdown syntax like **bold**, *italic*, `code`, etc.
 */
const MarkdownRenderer = ({ content, className = "" }) => {
  if (!content) return null;

  const renderMarkdown = (text) => {
    let result = text;

    // Handle code blocks first (```)
    result = result.replace(/```([\s\S]*?)```/g, (match, code) => {
      return `<pre class="bg-gray-100 border rounded-md p-3 my-2 overflow-x-auto"><code class="text-sm font-mono text-gray-800">${code.trim()}</code></pre>`;
    });

    // Handle inline code (`)
    result = result.replace(/`([^`]+)`/g, '<code class="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono text-gray-800">$1</code>');

    // Handle bold text (**)
    result = result.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>');

    // Handle italic text (*)
    result = result.replace(/(?<!\*)\*(?!\*)([^*]+)(?<!\*)\*(?!\*)/g, '<em class="italic">$1</em>');

    // Handle links [text](url)
    result = result.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-blue-600 hover:text-blue-800 underline" target="_blank" rel="noopener noreferrer">$1</a>');

    // Handle headers
    result = result.replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold mt-4 mb-2 text-gray-800">$1</h3>');
    result = result.replace(/^## (.*$)/gm, '<h2 class="text-xl font-semibold mt-4 mb-2 text-gray-800">$1</h2>');
    result = result.replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-4 mb-2 text-gray-900">$1</h1>');

    // Handle bullet points
    result = result.replace(/^\* (.*)$/gm, '<li class="ml-4 mb-1">• $1</li>');
    result = result.replace(/^- (.*)$/gm, '<li class="ml-4 mb-1">• $1</li>');

    // Handle numbered lists
    result = result.replace(/^\d+\. (.*)$/gm, (match, text, offset, string) => {
      const lines = string.substring(0, offset).split('\n');
      const currentLine = lines.length;
      const number = lines.filter(line => /^\d+\./.test(line)).length + 1;
      return `<li class="ml-4 mb-1">${number}. ${text}</li>`;
    });

    // Handle line breaks
    result = result.replace(/\n\n/g, '</p><p class="mb-3">');
    result = result.replace(/\n/g, '<br>');

    // Wrap in paragraph tags
    result = `<p class="mb-3">${result}</p>`;

    // Clean up empty paragraphs
    result = result.replace(/<p class="mb-3"><\/p>/g, '');

    return result;
  };

  return (
    <div 
      className={`prose prose-sm max-w-none ${className}`}
      dangerouslySetInnerHTML={{ 
        __html: renderMarkdown(content) 
      }} 
    />
  );
};

export default MarkdownRenderer;
