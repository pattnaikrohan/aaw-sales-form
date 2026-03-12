const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function apiCall(endpoint, data) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    let errorMsg = `HTTP ${response.status}`;
    try {
      const errorData = await response.json();
      if (typeof errorData.detail === 'string') {
        errorMsg = errorData.detail;
      } else if (Array.isArray(errorData.detail)) {
        errorMsg = errorData.detail[0]?.msg || 'Validation Error';
      } else if (errorData.message) {
        errorMsg = errorData.message;
      }
    } catch (e) {
      // Fallback
    }
    throw new Error(errorMsg);
  }

  return response.json();
}

export async function searchCompany(companySearchText) {
  return apiCall('/company-search', { companySearchText });
}

export async function sendChatMessage(message, conversationHistory, currentFormState) {
  return apiCall('/chat', { message, conversationHistory, currentFormState });
}

export async function extractFieldsFromChat(userMessage, botReply, currentFormState) {
  return apiCall('/extract-fields', { userMessage, botReply, currentFormState });
}

export async function processSpeech(name, contentBytes) {
  return apiCall('/speech', { name, contentBytes });
}

export async function submitForm(formData) {
  return apiCall('/submit', formData);
}

export async function healthCheck() {
  const response = await fetch(`${API_BASE}/health`);

  if (!response.ok) {
    throw new Error(`Backend error: ${response.status}`);
  }

  const text = await response.text();

  try {
    return JSON.parse(text);
  } catch {
    throw new Error("Backend returned non-JSON response");
  }
}

export async function login(email, password) {
  return apiCall('/auth/login', { email, password });
}

export async function register(name, email, password) {
  return apiCall('/auth/register', { name, email, password });
}

export async function getCurrentUser(token) {
  const response = await fetch(`${API_BASE}/auth/me?token=${token}`);
  if (!response.ok) throw new Error('Invalid token');
  return response.json();
}
