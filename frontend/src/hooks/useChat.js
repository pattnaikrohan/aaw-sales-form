import { useState, useCallback } from 'react';
import { sendChatMessage } from '../services/api';

export default function useChat(formData, updateMultipleFields) {
    const [messages, setMessages] = useState([]);
    const [isTyping, setIsTyping] = useState(false);
    const [error, setError] = useState(null);

    const sendMessage = useCallback(
        async (text) => {
            if (!text.trim()) return;

            const newUserMessage = { role: 'user', content: text };

            // Update local state immediately with user message
            setMessages((prev) => [...prev, newUserMessage]);
            setIsTyping(true);
            setError(null);

            try {
                // Send to backend (backend handles history and prompt)
                const result = await sendChatMessage(text, messages, formData);

                // Add assistant reply
                const newAssistantMessage = {
                    role: 'assistant',
                    content: result.reply,
                };
                setMessages((prev) => [...prev, newAssistantMessage]);

                // Auto-fill form fields
                if (result.extractedFields && Object.keys(result.extractedFields).length > 0) {
                    updateMultipleFields(result.extractedFields);
                }
            } catch (err) {
                setError(`Failed to send message: ${err.message}`);
                setMessages((prev) => [
                    ...prev,
                    { role: 'assistant', content: 'Sorry, I encountered an error processing your message.' }
                ]);
            } finally {
                setIsTyping(false);
            }
        },
        [messages, formData, updateMultipleFields]
    );

    return {
        messages,
        isTyping,
        error,
        sendMessage,
    };
}
