import { PublicClientApplication } from '@azure/msal-browser';

export const msalConfig = {
    auth: {
        // REPLACE THIS WITH YOUR CLIENT ID
        clientId: '399823b9-a4a1-4a1a-b0e3-8aa68510e2d2',

        // REPLACE THIS WITH YOUR TENANT ID (or leave common for multi-tenant)
        authority: 'https://login.microsoftonline.com/9a3bb301-12fd-4106-a7f7-563f72cfdf69',

        // The URL where MSAL redirects after login (must match Entra ID app registration)
        // Using window.location.origin dynamically handles if Vite starts on port 5174, 5175, etc.
        redirectUri: typeof window !== "undefined" ? window.location.origin : 'http://localhost:5173',
    },
    cache: {
        cacheLocation: 'sessionStorage',
        storeAuthStateInCookie: false,
    }
};

export const loginRequest = {
    // Requires CopilotStudio.Copilots.Invoke API Permission in Entra ID
    scopes: ['https://api.powerplatform.com/.default']
};

export const msalInstance = new PublicClientApplication(msalConfig);
