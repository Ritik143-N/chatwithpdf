import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import ChatBox from './components/ChatBox';
import EnhancedDocumentViewer from './components/EnhancedDocumentViewer';
import SessionManager from './components/SessionManager';
import Navbar from './components/Navbar';
import { createSession, getSessionDetails } from './services/api';
import './App.css';

function App() {
  const [uploadedDocument, setUploadedDocument] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [sessionData, setSessionData] = useState(null);
  const [showSessionManager, setShowSessionManager] = useState(true);

  // Handle URL-based session navigation
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session');
    
    if (sessionId && sessionId !== currentSessionId) {
      loadSession(sessionId);
    }
  }, [currentSessionId]);

  const loadSession = async (sessionId) => {
    try {
      console.log('Loading session:', sessionId);
      const sessionDetails = await getSessionDetails(sessionId);      
      setCurrentSessionId(sessionId);
      setSessionData(sessionDetails);
      
      // Update URL without page reload
      const newUrl = `${window.location.pathname}?session=${sessionId}`;
      window.history.pushState({ sessionId }, '', newUrl);
      
      // Set the document from session data
      if (sessionDetails.session && sessionDetails.session.document_id) {
        const sessionDoc = sessionDetails.session;
        const documentData = {
          doc_id: sessionDoc.document_id,
          filename: sessionDoc.document_filename,
          message: `Document: ${sessionDoc.document_name || sessionDoc.document_filename}`,
          fromSession: true  // Add this flag so EnhancedDocumentViewer knows this is a session document
        };
        console.log('Setting document from session:', documentData);
        setUploadedDocument(documentData);
        // Clear the uploaded file since we don't have the original file for session documents
        setUploadedFile(null);
      } else {
        console.log('No document_id in session details');
        setUploadedDocument(null);
        setUploadedFile(null);
      }
    } catch (error) {
      console.error('Error loading session:', error);
      alert('Failed to load session');
    }
  };

  const handleUploadSuccess = async (response, file) => {
    try {
      // Create a new session for this document
      const session = await createSession(
        response.doc_id,
        response.filename,
        file.name
      );
      
      setUploadedDocument(response);
      setUploadedFile(file);
      setShowUploadModal(false);
      setCurrentSessionId(session.session_id);
      setSessionData(session);
      
      // Update URL with new session
      const newUrl = `${window.location.pathname}?session=${session.session_id}`;
      window.history.pushState({ sessionId: session.session_id }, '', newUrl);
      
      console.log('Document uploaded and session created:', response, session);
    } catch (error) {
      console.error('Error creating session:', error);
      // Fallback to old behavior if session creation fails
      setUploadedDocument(response);
      setUploadedFile(file);
      setShowUploadModal(false);
    }
  };

  const handleSessionSelect = (sessionId) => {
    if (sessionId !== currentSessionId) {
      loadSession(sessionId);
    }
  };

  const handleNewSession = () => {
    setCurrentSessionId(null);
    setSessionData(null);
    setUploadedDocument(null);
    setUploadedFile(null);
    
    // Clear URL parameters
    window.history.pushState({}, '', window.location.pathname);
    
    // Show upload modal to start new session
    setShowUploadModal(true);
  };

  const handleUploadClick = () => {
    setShowUploadModal(true);
  };

  const toggleSessionManager = () => {
    setShowSessionManager(!showSessionManager);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Bar */}
      <Navbar 
        onUploadClick={handleUploadClick} 
        onToggleSessionManager={toggleSessionManager}
        showSessionManager={showSessionManager}
      />
      
      <div className="flex h-screen pt-16"> {/* pt-16 to account for fixed navbar */}
        {/* Session Manager Panel */}
        {showSessionManager && (
          <div className="w-80 border-r border-gray-200 bg-white">
            <SessionManager
              currentSessionId={currentSessionId}
              onSessionSelect={handleSessionSelect}
              onNewSession={handleNewSession}
            />
          </div>
        )}

        {/* Left Panel - Document Viewer */}
        <div className={`${showSessionManager ? 'w-1/2' : 'w-1/2'} border-r border-gray-200 bg-white`}>
          <EnhancedDocumentViewer document={uploadedDocument} uploadedFile={uploadedFile} />
        </div>

        {/* Right Panel - Chat Interface */}
        <div className={`${showSessionManager ? 'w-1/2' : 'w-1/2'} bg-white`}>
          <ChatBox 
            uploadedDocument={uploadedDocument} 
            currentSessionId={currentSessionId}
            sessionData={sessionData}
          />
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Upload Document</h2>
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
