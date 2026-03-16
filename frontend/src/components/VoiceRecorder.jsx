import React from 'react';

export default function VoiceRecorder({
    isRecording,
    isProcessing,
    audioURL,
    recordingTime,
    error,
    onStart,
    onStop,
    formatTime,
}) {
    return (
        <div className="voice-section">
            <div className="voice-recorder">
                <button
                    className={`mic-button ${isRecording ? 'recording' : isProcessing ? 'processing' : 'idle'
                        }`}
                    onClick={isRecording ? onStop : onStart}
                    disabled={isProcessing}
                    title={isRecording ? 'Stop Recording' : 'Start Recording'}
                >
                    {isRecording ? (
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <rect width="16" height="16" x="4" y="4" rx="3" ry="3" />
                        </svg>
                    ) : isProcessing ? (
                        <span className="spinner"></span>
                    ) : (
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                            <line x1="12" x2="12" y1="19" y2="22" />
                        </svg>
                    )}
                </button>

                <div className="voice-status">
                    <span className="voice-status-text">
                        {isRecording
                            ? 'Recording...'
                            : isProcessing
                                ? 'Extracting details...'
                                : audioURL
                                    ? 'Recording complete'
                                    : 'Record meeting summary'}
                    </span>
                    <span className="voice-status-sub">
                        {isRecording
                            ? 'Speak naturally'
                            : isProcessing
                                ? 'Processing with AAW AI'
                                : 'Click mic to start'}
                    </span>
                </div>

                {isRecording && (
                    <div className="voice-timer">
                        {formatTime(recordingTime)}
                    </div>
                )}

                {audioURL && !isRecording && !isProcessing && (
                    <div className="audio-player">
                        <audio src={audioURL} controls controlsList="nodownload noplaybackrate" />
                    </div>
                )}
            </div>

            {error && <div className="error-message" style={{ marginTop: '8px' }}>{error}</div>}
        </div>
    );
}
