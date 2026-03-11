import { useState, useCallback, useRef } from 'react';
import { processSpeech } from '../services/api';

export default function useVoice(updateMultipleFields) {
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [audioURL, setAudioURL] = useState(null);
    const [recordingTime, setRecordingTime] = useState(0);
    const [error, setError] = useState(null);

    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const timerRef = useRef(null);

    const startRecording = useCallback(async () => {
        try {
            setError(null);
            setAudioURL(null);
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    audioChunksRef.current.push(e.data);
                }
            };

            mediaRecorder.onstop = async () => {
                // Stop all tracks
                stream.getTracks().forEach((track) => track.stop());
                clearInterval(timerRef.current);

                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                const url = URL.createObjectURL(audioBlob);
                setAudioURL(url);

                // Convert to base64 and send to backend
                setIsProcessing(true);
                try {
                    const reader = new FileReader();
                    const base64Promise = new Promise((resolve, reject) => {
                        reader.onloadend = () => {
                            const base64 = reader.result.split(',')[1];
                            resolve(base64);
                        };
                        reader.onerror = reject;
                    });
                    reader.readAsDataURL(audioBlob);
                    const contentBytes = await base64Promise;

                    const result = await processSpeech('speech.webm', contentBytes);

                    // Map response fields to formData fields
                    const fieldMap = {};
                    if (result.clientname) fieldMap.clientName = result.clientname;
                    if (result.subject) fieldMap.subject = result.subject;
                    if (result.method) fieldMap.method = result.method;
                    if (result.purpose) fieldMap.purpose = result.purpose;
                    if (result.status) fieldMap.status = result.status;
                    if (result.primarycontact) fieldMap.primaryContact = result.primarycontact;
                    if (result.actualdate) fieldMap.actualDate = result.actualdate;
                    if (result.notes) fieldMap.notes = result.notes;

                    if (Object.keys(fieldMap).length > 0) {
                        updateMultipleFields(fieldMap);
                    }
                } catch (err) {
                    setError(`Voice processing failed: ${err.message}`);
                } finally {
                    setIsProcessing(false);
                }
            };

            mediaRecorder.start(250);
            setIsRecording(true);
            setRecordingTime(0);
            timerRef.current = setInterval(() => {
                setRecordingTime((prev) => prev + 1);
            }, 1000);
        } catch (err) {
            setError('Microphone access denied. Please allow microphone access.');
        }
    }, [updateMultipleFields]);

    const stopRecording = useCallback(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    }, []);

    const formatTime = (seconds) => {
        const m = Math.floor(seconds / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    };

    return {
        isRecording,
        isProcessing,
        audioURL,
        recordingTime,
        error,
        startRecording,
        stopRecording,
        formatTime,
    };
}
