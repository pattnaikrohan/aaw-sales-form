import React, { useEffect, useMemo, useRef, useState } from 'react';
import ReactWebChat, { createStore } from 'botframework-webchat';
import { useMsal } from '@azure/msal-react';
import { loginRequest } from '../authConfig';

// Both client and webchat connection wrapper are bundled in this single package
import {
    CopilotStudioClient,
    ConnectionSettings,
    CopilotStudioWebChat
} from '@microsoft/agents-copilotstudio-client';

/**
 * Convert a date string like "3/11/2026" (M/D/YYYY) to "2026-03-11" (YYYY-MM-DD)
 */
function parseDateToISO(dateStr) {
    if (!dateStr) return null;
    // Try M/D/YYYY format
    const mdyMatch = dateStr.trim().match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
    if (mdyMatch) {
        const month = mdyMatch[1].padStart(2, '0');
        const day = mdyMatch[2].padStart(2, '0');
        return `${mdyMatch[3]}-${month}-${day}`;
    }
    // Already YYYY-MM-DD
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr.trim())) {
        return dateStr.trim();
    }
    return null;
}

export default function ChatAssistant({ updateMultipleFields }) {
    const { instance, accounts } = useMsal();
    const [directLine, setDirectLine] = useState(null);
    const [error, setError] = useState(null);

    // Track which field the bot is currently asking about
    const pendingFieldRef = useRef(null);
    // Track the company options list for number-based selection
    const companyOptionsRef = useRef([]);

    // Bot Metadata retrieved from Copilot Studio -> Settings -> Advanced -> Metadata
    const botEnvironmentId = "Default-9a3bb301-12fd-4106-a7f7-563f72cfdf69";
    const botSchemaName = "auto_agent_7qXUb";

    // Create WebChat store with middleware to intercept messages
    const store = useMemo(() => createStore({}, ({ dispatch }) => next => action => {

        // ── USER sends a message ─────────────────────────────────────
        if (action.type === 'WEB_CHAT/SEND_MESSAGE') {
            const userText = action.payload?.text?.trim();
            const lowerText = userText?.toLowerCase();
            
            // Guard: Don't auto-fill if it's just a simple confirmation (Yes/No/Ok)
            // unless we really want those as values (rare for these fields).
            const isSimpleConfirmation = ['yes', 'no', 'ok', 'sure', 'y', 'n'].includes(lowerText);

            if (userText && pendingFieldRef.current && !isSimpleConfirmation) {
                const field = pendingFieldRef.current;

                if (field === 'companySelection') {
                    // User picked a number from the company list
                    const idx = parseInt(userText, 10) - 1;
                    const companies = companyOptionsRef.current;
                    if (!isNaN(idx) && companies[idx]) {
                        console.log('[ChatAssistant] Auto-fill clientName:', companies[idx]);
                        setTimeout(() => updateMultipleFields({ clientName: companies[idx] }), 0);
                    }
                } else {
                    console.log(`[ChatAssistant] Auto-fill ${field}:`, userText);
                    setTimeout(() => updateMultipleFields({ [field]: userText }), 0);
                }

                pendingFieldRef.current = null;
            }
        }

        // ── BOT incoming message ─────────────────────────────────────
        if (action.type === 'DIRECT_LINE/INCOMING_ACTIVITY') {
            const activity = action.payload?.activity;
            if (
                activity &&
                activity.type === 'message' &&
                activity.from?.role === 'bot' &&
                activity.text
            ) {
                const text = activity.text;

                // Reset pending field - we only want to track it if THIS message is a question
                pendingFieldRef.current = null;

                // ── Parse bot confirmation messages ──────────────────
                const fieldsFromBot = {};

                // "Scheduled Date: 3/11/2026"
                const schedMatch = text.match(/Scheduled\s+Date\s*:\s*(\S+)/i);
                if (schedMatch) {
                    const iso = parseDateToISO(schedMatch[1]);
                    if (iso) fieldsFromBot.scheduledDate = iso;
                }

                // "Actual Date : 3/11/2026"
                const actualMatch = text.match(/Actual\s+Date\s*:\s*(\S+)/i);
                if (actualMatch) {
                    const iso = parseDateToISO(actualMatch[1]);
                    if (iso) fieldsFromBot.actualDate = iso;
                }

                // 'The notes have been recorded as: **"Amazing, the call went great"**'
                const notesMatch = text.match(/notes\s+have\s+been\s+recorded\s+as\s*:\s*\*{0,2}"?([^"*]+)"?\*{0,2}/i);
                if (notesMatch) {
                    fieldsFromBot.notes = notesMatch[1].trim();
                }

                // Apply any confirmed fields
                if (Object.keys(fieldsFromBot).length > 0) {
                    console.log('[ChatAssistant] Auto-fill from bot confirmation:', fieldsFromBot);
                    setTimeout(() => updateMultipleFields(fieldsFromBot), 0);
                }

                // ── Detect what the bot is asking next ───────────────
                // Company list shown → next user response is a number selection
                if (/I found.*compan/i.test(text)) {
                    const lines = text.split('\n');
                    const options = [];
                    for (const line of lines) {
                        const optMatch = line.match(/^\s*\d+\.\s+(.+)/);
                        if (optMatch && optMatch[1].trim()) {
                            options.push(optMatch[1].trim());
                        }
                    }
                    if (options.length > 0) {
                        companyOptionsRef.current = options;
                        pendingFieldRef.current = 'companySelection';
                    }
                }
                // "Please select the number for the correct company name"
                else if (/select.*number.*company/i.test(text)) {
                    pendingFieldRef.current = 'companySelection';
                }
                // Question detection → set pending field for next user response
                else if (/enter\s+the\s+client\s*name/i.test(text) || /client\s*name/i.test(text) && /enter|type|provide/i.test(text)) {
                    pendingFieldRef.current = 'clientName';
                }
                else if (/purpose\s+(of|for)/i.test(text)) {
                    pendingFieldRef.current = 'purpose';
                }
                else if (/method\s+(of|for)/i.test(text)) {
                    pendingFieldRef.current = 'method';
                }
                else if (/primary\s*contact/i.test(text)) {
                    pendingFieldRef.current = 'primaryContact';
                }
                else if (/subject\s*(line|describing)/i.test(text)) {
                    pendingFieldRef.current = 'subject';
                }
                else if (/status\s+(of|for|this)/i.test(text) || /select.*status/i.test(text)) {
                    pendingFieldRef.current = 'status';
                }
                else if (/scheduled\s*date/i.test(text) && !schedMatch) {
                    pendingFieldRef.current = 'scheduledDate';
                }
                else if (/actual\s*date/i.test(text) && !actualMatch) {
                    pendingFieldRef.current = 'actualDate';
                }
                else if (/notes/i.test(text) && /describe|enter|provide|detail/i.test(text) && !notesMatch) {
                    pendingFieldRef.current = 'notes';
                }
            }
        }

        return next(action);
    }), [updateMultipleFields]);

    useEffect(() => {
        const initializeSDK = async () => {
            if (accounts.length === 0) return;

            try {
                // 1. Get the Entra ID Access Token scoped for powerplatform.com
                const tokenRequest = {
                    ...loginRequest,
                    account: accounts[0]
                };
                const authResponse = await instance.acquireTokenSilent(tokenRequest);
                const entraIdToken = authResponse.accessToken;

                // 2. Configure SDK Connection Settings
                const authConfig = instance.getConfiguration().auth;
                const tenantId = authConfig.authority.split('/').pop() || "common";

                const settings = new ConnectionSettings({
                    appClientId: authConfig.clientId,
                    tenantId: tenantId,
                    environmentId: botEnvironmentId,
                    agentIdentifier: botSchemaName
                });

                // 3. Initialize the Client with the Entra ID token
                const client = new CopilotStudioClient(settings, entraIdToken);

                // 4. Create the WebChat connection
                const connection = await CopilotStudioWebChat.createConnection(client, {
                    token: entraIdToken
                });

                setDirectLine(connection);
            } catch (err) {
                console.error("Error connecting via M365 Agents SDK:", err);

                if (err.name === 'InteractionRequiredAuthError') {
                    setError("Admin consent or login interaction required to access 'CopilotStudio.Copilots.Invoke'.");
                } else if (err.message && err.message.includes("fetch")) {
                    setError("Network issue: Unable to reach Copilot Studio.");
                } else {
                    setError(err.message || "Failed to initialize Microsoft 365 Agents SDK.");
                }
            }
        };

        initializeSDK();
    }, [accounts, instance]);

    // Customize the WebChat UI to match our AAW Blue Theme
    const styleOptions = useMemo(() => ({
        botAvatarInitials: 'AAW',
        userAvatarInitials: 'Me',
        primaryFont: "'Plus Jakarta Sans', 'Inter', sans-serif",
        bubbleBackground: '#f1f5f9',
        bubbleBorderRadius: 12,
        bubbleTextColor: '#334155',
        bubbleFromUserBackground: '#3b82f6',
        bubbleFromUserBorderRadius: 12,
        bubbleFromUserTextColor: 'white',
        sendBoxButtonColor: '#3b82f6',
        sendBoxButtonColorOnHover: '#2563eb',
        sendBoxHeight: 50,
        backgroundColor: 'transparent'
    }), []);

    return (
        <div className="panel-right" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="chat-header" style={{ flexShrink: 0 }}>
                <div className="chat-header-icon">✨</div>
                <div className="chat-header-text">
                    <h2>AAW Sales Assistant</h2>
                    <span>Powered by AAW AI</span>
                </div>
            </div>

            <div className="chat-body-container" style={{ flexGrow: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                {error ? (
                    <div className="chat-error-message" style={{ margin: '20px', padding: '15px', background: '#fee2e2', color: '#b91c1c', borderRadius: '8px', border: '1px solid #fca5a5' }}>
                        <strong>Connection Error:</strong> {error}
                        <div style={{ marginTop: '10px', fontSize: '13px' }}>
                            Ensure the Entra ID App ({instance.getConfiguration().auth.clientId}) has been granted <strong>CopilotStudio.Copilots.Invoke</strong> permission.
                        </div>
                    </div>
                ) : directLine ? (
                    <ReactWebChat
                        directLine={directLine}
                        store={store}
                        styleOptions={styleOptions}
                        className="react-webchat-container"
                    />
                ) : (
                    <div className="chat-loading" style={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '15px' }}>
                        <div className="loading-spinner" style={{ borderTopColor: '#3b82f6', width: '30px', height: '30px' }}></div>
                        <span style={{ color: 'var(--text-secondary)' }}>Connecting to Corporate Copilot via SDK...</span>
                    </div>
                )}
            </div>
        </div>
    );
}
