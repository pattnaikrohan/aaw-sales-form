import React, { useEffect, useState } from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import useFormState from './hooks/useFormState';
import useVoice from './hooks/useVoice';
import { healthCheck } from './services/api';

import SalesForm from './components/SalesForm';
import VoiceRecorder from './components/VoiceRecorder';
import ChatAssistant from './components/ChatAssistant';
import AuthPanel from './components/AuthPanel';
import './styles/app.css';
import aawLogo from './assets/aaw.png';

export default function App() {
  const [isBackendConnected, setIsBackendConnected] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [isChatOpen, setIsChatOpen] = useState(false);

  // MSAL hooks
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const currentUser = accounts.length > 0 ? accounts[0].name : 'User';

  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.remove('light-theme');
    } else {
      document.body.classList.add('light-theme');
    }
  }, [isDarkMode]);

  // Initialize shared state
  const { formData, updateField, updateMultipleFields, resetForm, autoFilledFields } = useFormState();

  // Initialize voice hook (updates shared state)
  const voice = useVoice(updateMultipleFields);

  // Check backend health on load
  useEffect(() => {
    const checkConnection = async () => {
      try {
        await healthCheck();
        setIsBackendConnected(true);
      } catch (err) {
        console.warn('Backend connection failed:', err);
        setIsBackendConnected(false);
      }
    };
    checkConnection();
  }, []);

  const handleLogout = () => {
    // Use MSAL logout redirect so it clears the Microsoft cookie
    instance.logoutRedirect({
      postLogoutRedirectUri: "http://localhost:5173/"
    });
  };

  const logoBase64 = aawLogo;

  if (!isAuthenticated) {
    return (
      <div className="app-container" style={{ position: 'relative' }}>
        <div className="toast-container" style={{ zIndex: 99999, top: '24px' }}>
          {!isBackendConnected && (
            <div className="toast warning">⚠️ Backend not connected</div>
          )}
        </div>
        <AuthPanel logoBase64={logoBase64} />
      </div>
    );
  }

  return (
    <div className="app-container">
      {!isBackendConnected && (
        <div className="toast-container" style={{ zIndex: 99999 }}>

        </div>
      )}

      {/* LEFT PANEL - Form & Voice */}
      <div className="panel-left">
        <header className="header">
          <div className="header-brand" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <img src={logoBase64} alt="AAW Group Logo" className="header-logo" style={{ marginBottom: 0 }} />
            <div className="header-title">
              <h1>SALES CALL RECORD</h1>
            </div>
          </div>

          <div className="header-actions">
            <button
              type="button"
              className={`chat-toggle-btn ${isChatOpen ? 'active' : ''}`}
              onClick={() => setIsChatOpen(!isChatOpen)}
              title={isChatOpen ? "Close Assistant" : "Open Assistant"}
            >
              <span className="icon">✨</span>
              <span className="text">AI Assistant</span>
            </button>

            <button
              type="button"
              className="btn theme-toggle-btn"
              onClick={() => setIsDarkMode(!isDarkMode)}
              title={isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
            >
              <span className="theme-icon">{isDarkMode ? '☀️' : '🌙'}</span>
              <span className="text">{isDarkMode ? 'Light Mode' : 'Dark Mode'}</span>
            </button>

            <div className="header-divider" />

            <div className="header-badge header-user-badge" onClick={handleLogout} title="Click to logout" style={{ cursor: 'pointer' }}>
              <span className="dot" style={{ background: '#3b82f6', boxShadow: '0 0 6px rgba(59,130,246,0.6)' }}></span>
              {currentUser}
              <span className="user-label">LOGOUT</span>
            </div>
            <div className="header-badge header-status-badge">
              <span className="dot"></span> Online
            </div>
          </div>
        </header>

        <VoiceRecorder
          isRecording={voice.isRecording}
          isProcessing={voice.isProcessing}
          audioURL={voice.audioURL}
          recordingTime={voice.recordingTime}
          error={voice.error}
          onStart={voice.startRecording}
          onStop={voice.stopRecording}
          formatTime={voice.formatTime}
        />

        <SalesForm
          formData={formData}
          updateField={updateField}
          resetForm={resetForm}
          autoFilledFields={autoFilledFields}
        />
      </div >

      {/* RIGHT PANEL - Chat Assistant (Collapsible) */}
      {
        isChatOpen && (
          <ChatAssistant
            updateMultipleFields={updateMultipleFields}
          />
        )
      }
    </div >
  );
}
