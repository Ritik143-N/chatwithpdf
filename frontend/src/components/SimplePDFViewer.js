import React, { useState, useEffect } from 'react';

const DocumentViewer = ({ uploadedFile, document }) => {
  const [pdfUrl, setPdfUrl] = useState(null);
  const [fileType, setFileType] = useState(null);

  useEffect(() => {
    if (uploadedFile) {
      // Create a blob URL from the uploaded file
      const url = URL.createObjectURL(uploadedFile);
      setPdfUrl(url);
      
      // Determine file type
      const extension = uploadedFile.name.split('.').pop().toLowerCase();
      setFileType(extension);
      
      // Cleanup function to revoke the URL when component unmounts
      return () => URL.revokeObjectURL(url);
    }
  }, [uploadedFile]);

  const getFileIcon = (extension) => {
    const icons = {
      'pdf': '📄',
      'docx': '📝',
      'doc': '📝', 
      'pptx': '📊',
      'ppt': '📊',
      'xlsx': '📗',
      'xls': '📗',
      'txt': '📄',
      'rtf': '📝',
      'md': '📄',
      'csv': '📊'
    };
    return icons[extension] || '📄';
  };

  const getFileTypeDescription = (extension) => {
    const descriptions = {
      'pdf': 'PDF Document',
      'docx': 'Word Document',
      'doc': 'Word Document (Legacy)',
      'pptx': 'PowerPoint Presentation',
      'ppt': 'PowerPoint Presentation (Legacy)',
      'xlsx': 'Excel Spreadsheet',
      'xls': 'Excel Spreadsheet (Legacy)',
      'txt': 'Text File',
      'rtf': 'Rich Text Document',
      'md': 'Markdown File',
      'csv': 'CSV File'
    };
    return descriptions[extension] || 'Document';
  };

  // If no document uploaded, show empty state
  if (!uploadedFile && !document) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-gray-400 p-8">
        <svg className="w-24 h-24 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 className="text-xl font-medium text-gray-500 mb-2">No document loaded</h3>
        <p className="text-gray-400 text-center">
          Upload a document (PDF, DOCX, PPTX, TXT, etc.) to view it here and start chatting with its content.
        </p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-gray-200 bg-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">
                {fileType ? getFileIcon(fileType) : '📄'}
              </span>
            </div>
            <div>
              <h2 className="text-lg font-medium text-gray-900 truncate max-w-64">
                {uploadedFile ? uploadedFile.name : 'Document'}
              </h2>
              <p className="text-sm text-gray-500">
                {uploadedFile ? `${getFileTypeDescription(fileType)} • ${(uploadedFile.size / 1024 / 1024).toFixed(2)} MB` : 'Document loaded'}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => window.open(pdfUrl, '_blank')}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              disabled={!pdfUrl}
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              Open in New Tab
            </button>
          </div>
        </div>
      </div>

      {/* Document Viewer */}
      <div className="flex-1 flex flex-col">
        {pdfUrl && fileType === 'pdf' ? (
          // PDF Viewer
          <div className="flex-1 relative">
            <iframe
              src={`${pdfUrl}#toolbar=1&navpanes=1&scrollbar=1&page=1&view=FitH`}
              className="w-full h-full border-0"
              title="PDF Viewer"
              style={{
                minHeight: '600px',
                backgroundColor: '#f5f5f5'
              }}
            />
          </div>
        ) : fileType && fileType !== 'pdf' ? (
          // Non-PDF Document Display
          <div className="flex-1 overflow-auto p-6 bg-gray-50">
            <div className="max-w-4xl mx-auto">
              <div className="bg-white shadow-lg rounded-lg p-6 mb-6">
                <div className="flex items-center justify-center h-32 border-2 border-dashed border-gray-300 rounded-lg mb-4">
                  <div className="text-center">
                    <span className="text-4xl mb-2 block">
                      {getFileIcon(fileType)}
                    </span>
                    <h3 className="text-lg font-medium text-gray-900 mb-1">
                      {getFileTypeDescription(fileType)} Processed
                    </h3>
                    <p className="text-sm text-gray-500">
                      Document content extracted and ready for AI chat
                    </p>
                  </div>
                </div>
                
                <div className="border-t pt-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-600">File Type:</span>
                      <span className="ml-2 text-gray-900">{getFileTypeDescription(fileType)}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-600">Size:</span>
                      <span className="ml-2 text-gray-900">
                        {uploadedFile ? `${(uploadedFile.size / 1024 / 1024).toFixed(2)} MB` : 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <h4 className="text-md font-medium text-gray-900 mb-3">
                  💬 Start Chatting with Your Document
                </h4>
                <div className="text-sm text-gray-600 space-y-2">
                  <p>• Ask questions about the document content</p>
                  <p>• Request summaries or specific information</p>
                  <p>• Get insights and analysis</p>
                </div>
                
                {fileType !== 'pdf' && (
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="flex">
                      <svg className="w-5 h-5 text-blue-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                      <div className="ml-3 text-sm text-blue-700">
                        <p>
                          Non-PDF documents are processed by extracting their text content. 
                          Original formatting may not be preserved in the preview, but all content is available for chat.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          // Fallback content display
          <div className="flex-1 overflow-auto p-4">
            <div className="max-w-4xl mx-auto">
              {/* Document Info Card */}
              <div className="bg-white shadow-lg rounded-lg p-6 mb-6">
                <div className="flex items-center justify-center h-32 border-2 border-dashed border-gray-300 rounded-lg mb-4">
                  <div className="text-center">
                    <svg className="mx-auto h-10 w-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 className="mt-2 text-sm font-medium text-gray-900">PDF Document Ready</h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Document processed and ready for chat
                    </p>
                  </div>
                </div>
              </div>
              
              {/* Text Content */}
              {document && document.content && (
                <div className="bg-white shadow-lg rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">Document Content</h3>
                    <div className="flex items-center text-sm text-gray-500">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V9a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                      Text Extracted
                    </div>
                  </div>
                  <div className="prose prose-sm max-w-none">
                    <div className="text-gray-700 leading-relaxed text-sm border border-gray-200 rounded-lg p-6 bg-gray-50 font-mono whitespace-pre-wrap max-h-96 overflow-y-auto">
                      {document.content}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="flex-shrink-0 border-t border-gray-200 bg-white px-4 py-2">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-4">
            <span className="flex items-center text-green-600">
              <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Document Processed
            </span>
            <span className="flex items-center">
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
              Ready for Chat
            </span>
          </div>
          <div className="flex items-center space-x-4 text-gray-400">
            {pdfUrl ? (
              <span>📄 PDF Viewer • Text Selectable • Zoom Available</span>
            ) : (
              <span>� Text Content Available for Chat</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;
