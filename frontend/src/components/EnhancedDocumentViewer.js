import React, { useState, useEffect } from 'react';
import { getDocumentContent } from '../services/api';

const EnhancedDocumentViewer = ({ uploadedFile, document }) => {
  const [pdfUrl, setPdfUrl] = useState(null);
  const [fileType, setFileType] = useState(null);
  const [documentContent, setDocumentContent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(100);

  useEffect(() => {
    console.log('EnhancedDocumentViewer useEffect triggered:', { uploadedFile: !!uploadedFile, document });
    
    if (uploadedFile) {
      const url = URL.createObjectURL(uploadedFile);
      setPdfUrl(url);
      
      const extension = uploadedFile.name.split('.').pop().toLowerCase();
      setFileType(extension);
      
      // Load document content for non-PDF files
      if (extension !== 'pdf' && document?.doc_id) {
        loadDocumentContent(document.doc_id);
      }
      
      return () => URL.revokeObjectURL(url);
    } else if (document && document.fromSession && document.doc_id) {
      // Handle session-based document loading (no original file)
      console.log('Loading session document:', document);
      const filename = document.filename || 'document';
      const extension = filename.split('.').pop().toLowerCase();
      setFileType(extension);
      
      // For session documents, always load content as text preview
      loadDocumentContent(document.doc_id);
      
      // Clear PDF URL since we don't have the original file
      setPdfUrl(null);
    } else {
      // Reset states when no document
      console.log('Resetting document states');
      setPdfUrl(null);
      setFileType(null);
      setDocumentContent(null);
    }
  }, [uploadedFile, document]);

  const loadDocumentContent = async (docId) => {
    setLoading(true);
    try {
      const content = await getDocumentContent(docId);
      setDocumentContent(content);
    } catch (error) {
      console.error('Error loading document content:', error);
    } finally {
      setLoading(false);
    }
  };

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

  // Empty state
  if (!uploadedFile && !document) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-gray-400 p-8">
        <svg className="w-24 h-24 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 className="text-xl font-medium text-gray-500 mb-2">No document loaded</h3>
        <p className="text-gray-400 text-center">
          Upload a document (PDF, DOCX, PPTX, TXT, etc.) to view it here and start chatting.
        </p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Document Header */}
      <div className="flex-shrink-0 border-b border-gray-200 bg-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">
                {fileType ? getFileIcon(fileType) : '📄'}
              </span>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 truncate max-w-64">
                {uploadedFile ? uploadedFile.name : (document?.filename || 'Document')}
              </h2>
              <p className="text-sm text-gray-500">
                {uploadedFile 
                  ? `${getFileTypeDescription(fileType)} • ${(uploadedFile.size / 1024 / 1024).toFixed(2)} MB` 
                  : document?.fromSession 
                    ? `${getFileTypeDescription(fileType)} • From session`
                    : 'Document loaded'
                }
                {documentContent && (
                  <span className="ml-2">• {documentContent.total_chunks} sections</span>
                )}
              </p>
            </div>
          </div>

          {/* Toolbar */}
          <div className="flex items-center space-x-2">
            {fileType === 'pdf' ? (
              <>
                <div className="flex items-center space-x-2 text-sm">
                  <button
                    onClick={() => setZoomLevel(Math.max(50, zoomLevel - 10))}
                    className="p-1 rounded hover:bg-gray-100"
                    title="Zoom out"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
                    </svg>
                  </button>
                  <span className="px-2 py-1 bg-gray-100 rounded text-xs">{zoomLevel}%</span>
                  <button
                    onClick={() => setZoomLevel(Math.min(200, zoomLevel + 10))}
                    className="p-1 rounded hover:bg-gray-100"
                    title="Zoom in"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                    </svg>
                  </button>
                </div>
              </>
            ) : null}
            
            {/* <button
              onClick={() => window.open(pdfUrl, '_blank')}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none"
              disabled={!pdfUrl && fileType === 'pdf'}
              title="Open in new tab"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              Open
            </button> */}
          </div>
        </div>
      </div>

      {/* Document Content */}
      <div className="flex-1 overflow-auto">
        {fileType === 'pdf' && pdfUrl ? (
          // PDF Viewer
          <div className="h-full relative">
            <iframe
              src={`${pdfUrl}#toolbar=1&navpanes=1&scrollbar=1&zoom=${zoomLevel}`}
              className="w-full h-full border-0"
              title="PDF Viewer"
              style={{
                minHeight: '600px',
                backgroundColor: '#f5f5f5'
              }}
            />
          </div>
        ) : (
          // Enhanced Non-PDF Document Preview
          <div className="h-full bg-gray-50">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <div className="flex items-center space-x-3">
                  <svg className="animate-spin h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="text-gray-600">Loading document preview...</span>
                </div>
              </div>
            ) : (
              // Fallback for when content can't be loaded
              <div className="max-w-4xl mx-auto p-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
                  <span className="text-6xl mb-4 block">{getFileIcon(fileType)}</span>
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">
                    {getFileTypeDescription(fileType)} Processed
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Document content has been extracted and processed for AI chat.
                  </p>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-blue-700 text-sm">
                      <strong>✨ Ready for Chat:</strong> You can now ask questions about this document's content, 
                      request summaries, or get specific information from the text.
                    </p>
                  </div>
                </div>
              </div>
            )}
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
              Processed & Ready
            </span>
            {documentContent && (
              <span>{documentContent.total_chunks} sections loaded</span>
            )}
          </div>
          <div className="flex items-center space-x-4 text-gray-400">
            <span>
              {fileType === 'pdf' ? '📄 PDF Viewer Active' : `📋 ${getFileTypeDescription(fileType)} Preview`}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedDocumentViewer;
