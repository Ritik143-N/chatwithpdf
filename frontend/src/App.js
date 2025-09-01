import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ChatBox from './components/ChatBox';
import DocumentViewer from './components/DocumentViewer';
import Navbar from './components/Navbar';
import './App.css';

function App() {
  const [uploadedDocument, setUploadedDocument] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);

  const handleUploadSuccess = (response) => {
    setUploadedDocument(response);
    setShowUploadModal(false);
    console.log('Document uploaded successfully:', response);
  };

  const handleUploadClick = () => {
    setShowUploadModal(true);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Bar */}
      <Navbar onUploadClick={handleUploadClick} />
      
      <div className="flex h-screen pt-16"> {/* pt-16 to account for fixed navbar */}
        {/* Left Panel - Document Viewer */}
        <div className="w-1/2 border-r border-gray-200 bg-white">
          <DocumentViewer document={uploadedDocument} />
        </div>

        {/* Right Panel - Chat Interface */}
        <div className="w-1/2 bg-white">
          <ChatBox uploadedDocument={uploadedDocument} />
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Upload PDF Document</h2>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
