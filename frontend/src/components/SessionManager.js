import React, { useState, useEffect } from 'react';
import { getSessions, deleteSession } from '../services/api';
import './SessionManager.css';

const SessionManager = ({ currentSessionId, onSessionSelect, onNewSession }) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const response = await getSessions(20, 0); // Get last 20 sessions
      setSessions(response.sessions || []);
      setError(null);
    } catch (err) {
      console.error('Error loading sessions:', err);
      setError('Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async (sessionId, event) => {
    event.stopPropagation(); // Prevent session selection when deleting
    
    if (!window.confirm('Are you sure you want to delete this session?')) {
      return;
    }

    try {
      await deleteSession(sessionId);
      await loadSessions(); // Reload sessions
      
      // If we deleted the current session, trigger new session creation
      if (sessionId === currentSessionId) {
        onNewSession();
      }
    } catch (err) {
      console.error('Error deleting session:', err);
      alert('Failed to delete session');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) {
      return 'Today';
    } else if (diffDays === 2) {
      return 'Yesterday';
    } else if (diffDays <= 7) {
      return `${diffDays - 1} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const getDocumentIcon = (filename) => {
    if (!filename) return '📄';
    const ext = filename.split('.').pop()?.toLowerCase();
    const icons = {
      pdf: '📕',
      doc: '📘',
      docx: '📘',
      txt: '📝',
      md: '📋',
      csv: '📊',
      xlsx: '📗',
      xls: '📗'
    };
    return icons[ext] || '📄';
  };

  if (loading) {
    return (
      <div className="session-manager loading">
        <div className="loading-spinner">Loading sessions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="session-manager error">
        <div className="error-message">{error}</div>
        <button onClick={loadSessions} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  const displaySessions = showAll ? sessions : sessions.slice(0, 10);

  return (
    <div className="session-manager">
      <div className="session-header">
        <h3>Chat Sessions</h3>
        <button onClick={onNewSession} className="new-session-button">
          + New Chat
        </button>
      </div>

      <div className="sessions-list">
        {displaySessions.length === 0 ? (
          <div className="no-sessions">
            <p>No chat sessions yet</p>
            <p>Upload a document to start a new session</p>
          </div>
        ) : (
          displaySessions.map((session) => (
            <div
              key={session.session_id}
              className={`session-item ${session.session_id === currentSessionId ? 'active' : ''}`}
              onClick={() => onSessionSelect(session.session_id)}
            >
              <div className="session-content">
                <div className="session-main">
                  <div className="document-info">
                    <span className="document-icon">
                      {getDocumentIcon(session.document_filename)}
                    </span>
                    <div className="document-details">
                      <div className="document-name">
                        {session.document_name || session.document_filename || 'Untitled Document'}
                      </div>
                      <div className="session-meta">
                        <span className="message-count">{session.message_count || 0} messages</span>
                        <span className="model-provider">{session.model_provider}</span>
                      </div>
                    </div>
                  </div>
                  <div className="session-date">
                    {formatDate(session.updated_at)}
                  </div>
                </div>
                
                <button
                  className="delete-session"
                  onClick={(e) => handleDeleteSession(session.session_id, e)}
                  title="Delete session"
                >
                  ×
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {sessions.length > 10 && (
        <div className="session-footer">
          <button
            onClick={() => setShowAll(!showAll)}
            className="show-all-button"
          >
            {showAll ? 'Show Less' : `Show All (${sessions.length})`}
          </button>
        </div>
      )}
    </div>
  );
};

export default SessionManager;
