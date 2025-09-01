import React from 'react';

const DocumentViewer = ({ document }) => {
  if (!document) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-gray-400 p-8">
        <svg className="w-24 h-24 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 className="text-xl font-medium text-gray-500 mb-2">No document loaded</h3>
        <p className="text-gray-400 text-center">
          Upload a PDF document to view it here and start chatting with its content.
        </p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Document Header */}
      <div className="flex-shrink-0 border-b border-gray-200 p-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-medium text-gray-900 truncate">
              Document: {document.doc_id.substring(0, 8)}...
            </h2>
            <p className="text-sm text-gray-500">
              Processed successfully
            </p>
          </div>
        </div>
      </div>

      {/* Document Content */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Document Preview</h3>
          <div className="prose prose-sm max-w-none">
            <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
              {document.content}
            </div>
          </div>
        </div>
      </div>

      {/* Document Stats */}
      <div className="flex-shrink-0 border-t border-gray-200 p-4">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>Document processed</span>
          <div className="flex items-center space-x-4">
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              PDF
            </span>
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Ready for chat
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;
