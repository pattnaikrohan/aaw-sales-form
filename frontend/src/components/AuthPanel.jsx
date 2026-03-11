import React, { useState } from 'react';
import { useMsal } from '@azure/msal-react';
import { InteractionStatus } from '@azure/msal-browser';
import { loginRequest } from '../authConfig';
import '../styles/app.css';

export default function AuthPanel({ onLogin, logoBase64 }) {
    const { instance, inProgress } = useMsal();
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [authLocked, setAuthLocked] = useState(false);

    const handleMicrosoftLogin = async () => {
        setError(null);
        setLoading(true);

        try {
            await instance.loginRedirect({
                ...loginRequest,
                prompt: 'select_account' // Forces the Microsoft login screen to appear and prompt for Authenticator MFA
            });
            // Code below here likely won't execute as the browser instantly navigates away
        } catch (err) {
            console.error("Microsoft Redirect failed", err);
            setError(err.message || 'An error occurred triggering the Microsoft redirect');
            setLoading(false);
        }
    };

    return (
        <div className="auth-wrapper">
            <div className="auth-card" style={{ padding: '40px 30px' }}>
                <div className="auth-header">
                    <img src={logoBase64} alt="AAW Logo" className="auth-logo" />
                    <h2>Single Sign-On
                    </h2>
                    <p style={{ marginTop: '12px', fontSize: '1.05rem', color: 'var(--text-secondary)' }}>
                        Sign in with your AAW account to start
                    </p>
                </div>

                <div className="auth-form" style={{ marginTop: '30px' }}>
                    {error && <div className="auth-error" style={{ marginBottom: '20px' }}>{error}</div>}

                    <button
                        type="button"
                        className="btn btn-primary auth-submit"
                        onClick={handleMicrosoftLogin}
                        disabled={loading}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '12px',
                            padding: '14px 20px',
                            fontSize: '1.1rem',
                            background: 'white',
                            color: '#333',
                            border: '1px solid #ccc',
                            boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                        }}
                    >
                        {loading ? 'Connecting to Microsoft...' : (
                            <>
                                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 21 21">
                                    <path fill="#f25022" d="M0 0h10v10H0z" />
                                    <path fill="#7fba00" d="M11 0h10v10H11z" />
                                    <path fill="#00a4ef" d="M0 11h10v10H0z" />
                                    <path fill="#ffb900" d="M11 11h10v10H11z" />
                                </svg>
                                <strong>Sign In with Microsoft</strong>
                            </>
                        )}
                    </button>

                    {loading && (
                        <div className="loading-spinner" style={{ margin: '20px auto 0', borderTopColor: '#00a4ef' }}></div>
                    )}
                </div>
            </div>
        </div>
    );
}
