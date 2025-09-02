import React, { useState, useCallback } from 'react';
import { Document, Page } from 'react-pdf';
import { pdfjs } from 'react-pdf/dist/esm/entry.webpack';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import './DocumentViewer.css';

// Set up PDF.js worker with proper version
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

const DocumentViewer = ({ document, uploadedFile }) => {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const onDocumentLoadSuccess = useCallback(({ numPages }) => {
    setNumPages(numPages);
    setLoading(false);
    setError(null);
  }, []);

  const onDocumentLoadError = useCallback((error) => {
    console.error('Error loading PDF:', error);
    setError('Failed to load PDF document');
    setLoading(false);
  }, []);

  const changePage = (offset) => {
    setPageNumber(prevPageNumber => {
      const newPage = prevPageNumber + offset;
      return Math.min(Math.max(1, newPage), numPages || 1);
    });
  };

  const goToPage = (page) => {
    const targetPage = Math.min(Math.max(1, page), numPages || 1);
    setPageNumber(targetPage);
  };

  const changeZoom = (zoomIn) => {
    setScale(prevScale => {
      const newScale = zoomIn ? prevScale * 1.2 : prevScale / 1.2;
      return Math.min(Math.max(0.5, newScale), 3.0);
    });
  };

  // If no document or file is uploaded
  if (!document && !uploadedFile) {
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
    <div className="h-full flex flex-col bg-gray-50">
      {/* Document Header with Controls */}
      <div className="flex-shrink-0 border-b border-gray-200 bg-white p-4">
        <div className="flex items-center justify-between">
          {/* Document Info */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-lg font-medium text-gray-900 truncate">
                {uploadedFile ? uploadedFile.name : `Document ${document?.doc_id?.substring(0, 8)}...`}
              </h2>
              <p className="text-sm text-gray-500">
                {numPages ? `${numPages} pages` : 'Processing...'}
              </p>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-2">
            {/* Zoom Controls */}
            <div className="flex items-center space-x-1 bg-gray-100 rounded-md p-1">
              <button
                onClick={() => changeZoom(false)}
                className="p-1 rounded text-gray-600 hover:text-gray-800 hover:bg-white"
                title="Zoom Out"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                </svg>
              </button>
              <span className="text-sm text-gray-600 min-w-[3rem] text-center">
                {Math.round(scale * 100)}%
              </span>
              <button
                onClick={() => changeZoom(true)}
                className="p-1 rounded text-gray-600 hover:text-gray-800 hover:bg-white"
                title="Zoom In"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Page Navigation */}
        {numPages && (
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-200">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => changePage(-1)}
                disabled={pageNumber <= 1}
                className="p-2 rounded-md text-gray-600 hover:text-gray-800 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Page</span>
                <input
                  type="number"
                  min="1"
                  max={numPages}
                  value={pageNumber}
                  onChange={(e) => goToPage(parseInt(e.target.value) || 1)}
                  className="w-16 px-2 py-1 text-sm border border-gray-300 rounded text-center"
                />
                <span className="text-sm text-gray-600">of {numPages}</span>
              </div>

              <button
                onClick={() => changePage(1)}
                disabled={pageNumber >= numPages}
                className="p-2 rounded-md text-gray-600 hover:text-gray-800 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => setScale(1.0)}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
              >
                Reset Zoom
              </button>
            </div>
          </div>
        )}
      </div>

      {/* PDF Viewer */}
      <div className="flex-1 overflow-auto bg-gray-100 p-4">
        <div className="flex justify-center">
          {uploadedFile ? (
            <Document
              file={uploadedFile}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={
                <div className="flex flex-col items-center justify-center p-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                  <p className="text-gray-600">Loading PDF...</p>
                </div>
              }
              error={
                <div className="flex flex-col items-center justify-center p-8 text-red-600">
                  <svg className="w-12 h-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p>Failed to load PDF</p>
                  <p className="text-sm text-gray-500 mt-2">Please try uploading the file again</p>
                </div>
              }
            >
              <Page
                pageNumber={pageNumber}
                scale={scale}
                className="shadow-lg bg-white"
                renderTextLayer={true}
                renderAnnotationLayer={true}
              />
            </Document>
          ) : (
            // Fallback to text view if no PDF file available
            <div className="max-w-4xl w-full bg-white shadow-lg rounded-lg p-8">
              <h3 className="text-xl font-medium text-gray-900 mb-6">Document Content</h3>
              <div className="prose prose-sm max-w-none">
                <div className="text-gray-700 whitespace-pre-wrap leading-relaxed font-mono text-sm border border-gray-200 rounded p-4 bg-gray-50">
                  {document?.content}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Status Bar */}
      <div className="flex-shrink-0 border-t border-gray-200 bg-white px-4 py-2">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-4">
            <span className="flex items-center">
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              PDF Document
            </span>
            <span className="flex items-center">
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Ready for Chat
            </span>
          </div>
          <div className="text-xs text-gray-400">
            Text is selectable • Use zoom controls above
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;
