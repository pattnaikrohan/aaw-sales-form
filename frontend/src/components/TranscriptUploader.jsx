import React, { useRef, useState } from 'react';
import { processTranscript } from '../services/api';

export default function TranscriptUploader({ updateMultipleFields }) {
    const [isOpen, setIsOpen] = useState(false);
    const [pasteText, setPasteText] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null);

    const handleOpen = () => setIsOpen(true);
    const handleClose = () => {
        setIsOpen(false);
        setPasteText('');
        setError(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    const handleProcessText = async (textToProcess) => {
        if (!textToProcess || !textToProcess.trim()) {
            setError('Please provide transcript text to process.');
            return;
        }

        setIsProcessing(true);
        setError(null);

        try {
            // Close the modal immediately so user sees the loading state on the main form
            setIsOpen(false);

            // Let App/UI show processing (we assume the custom hook or parent handles a global loading state, 
            // but for simplicity we'll just await here and update the fields. The UI will catch up when fields update,
            // or we could add a global loading state trigger. For now, the user requested an 'Analyzing...' state)

            // To simulate the 'Analyzing...' state in the main UI without complex prop drilling, 
            // we'll update the 'notes' field temporarily to show status.
            updateMultipleFields({ notes: "Analyzing your transcript..." });

            const result = await processTranscript(textToProcess);

            // Update all fields with the AI response
            updateMultipleFields({
                clientName: result.clientname || '',
                subject: result.subject || '',
                method: result.method || '',
                purpose: result.purpose || '',
                status: result.status || '',
                primaryContact: result.primarycontact || '',
                actualDate: result.actualdate || '',
                notes: result.notes || '', // Replaces the 'Analyzing...' text
            });

        } catch (err) {
            console.error('Transcript processing failed:', err);
            setError(err.message || 'Failed to process transcript. Please try again.');
            updateMultipleFields({ notes: "Error: Failed to process transcript." });
            setIsOpen(true); // Re-open modal to show error
        } finally {
            setIsProcessing(false);
        }
    };

    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async (event) => {
            const fileText = event.target.result;
            await handleProcessText(fileText);
        };
        reader.onerror = () => {
            setError('Failed to read the file.');
        };
        reader.readAsText(file);
    };

    const handlePasteSubmit = () => {
        handleProcessText(pasteText);
    };

    return (
        <div className="voice-section">
            <div className="voice-recorder transcript-trigger">
                {/* The trigger button matching the mic style */}
                <button
                    type="button"
                    className={`mic-button ${isProcessing ? 'processing' : 'idle'}`}
                    onClick={handleOpen}
                    disabled={isProcessing}
                    title="Upload Transcript"
                >
                    {isProcessing ? (
                        <span className="spinner"></span>
                    ) : (
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                            <polyline points="14 2 14 8 20 8" />
                            <line x1="16" y1="13" x2="8" y2="13" />
                            <line x1="16" y1="17" x2="8" y2="17" />
                            <line x1="10" y1="9" x2="8" y2="9" />
                        </svg>
                    )}
                </button>

                <div className="voice-status" style={{ cursor: 'pointer' }} onClick={!isProcessing ? handleOpen : undefined}>
                    <span className="voice-status-text">
                        {isProcessing ? 'Analyzing transcript...' : 'Upload Teams Transcript'}
                    </span>
                    <span className="voice-status-sub">
                        {isProcessing ? 'Processing with Azure AI' : 'Click to upload'}
                    </span>
                </div>
            </div>

            {/* The Modal */}
            {isOpen && (
                <div className="transcript-modal-overlay" onClick={handleClose}>
                    <div className="transcript-modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="transcript-modal-header">
                            <h3>Upload Transcript</h3>
                            <button className="transcript-modal-close" onClick={handleClose}>✕</button>
                        </div>

                        <div className="transcript-modal-body">
                            <p className="transcript-instruction">
                                Upload a Teams `.txt` or `.vtt` file, or paste your text directly.
                            </p>

                            <div className="transcript-upload-section">
                                <input
                                    type="file"
                                    accept=".txt,.vtt"
                                    ref={fileInputRef}
                                    style={{ display: 'none' }}
                                    onChange={handleFileUpload}
                                />
                                <button
                                    className="btn transcript-upload-btn"
                                    onClick={() => fileInputRef.current.click()}
                                    disabled={isProcessing}
                                >
                                    Choose File
                                </button>
                                <span className="transcript-divider">OR</span>
                            </div>

                            <textarea
                                className="form-textarea transcript-textarea"
                                placeholder="Paste your transcript text here..."
                                value={pasteText}
                                onChange={(e) => setPasteText(e.target.value)}
                                disabled={isProcessing}
                            />

                            {error && <div className="error-message transcript-error">{error}</div>}
                        </div>

                        <div className="transcript-modal-footer">
                            <button
                                className="btn transcript-cancel-btn"
                                onClick={handleClose}
                                disabled={isProcessing}
                            >
                                Cancel
                            </button>
                            <button
                                className="btn transcript-process-btn"
                                onClick={handlePasteSubmit}
                                disabled={isProcessing || !pasteText.trim()}
                            >
                                {isProcessing ? 'Processing...' : 'Process Text'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
