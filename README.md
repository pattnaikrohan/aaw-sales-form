# AAW Group React Sales App

This project consists of a React (Vite) frontend and a Python (FastAPI) backend.

## Prerequisites
- Node.js (for the frontend)
- Python 3.x (for the backend)

## How to Start the Application

You need to start **both** the backend and the frontend in separate terminal windows.

### 1. Start the Backend

Open a terminal, navigate to the `backend` folder, and start the FastAPI server:

```bash
cd "D:\Form + Chatbot\backend"
python -m uvicorn main:app --reload --port 8000
```
*The backend will be running at `http://localhost:8000`.*

### 2. Start the Frontend

Open a new terminal, navigate to the `frontend` folder, and start the React dev server:

```bash
cd "D:\Form + Chatbot\frontend"
npm run dev
```
*The frontend will be running at `http://localhost:5173`.*

## Environment Variables

Before using the app fully, ensure you configure the following in `D:\Form + Chatbot\backend\.env`:

```env
AZURE_FUNCTION_URL=https://azurespeechsdk-bphydzgsefggd9ev.australiaeast-01.azurewebsites.net/api/speechprocess
FLOW1_URL=<Power Automate Flow 1 HTTP trigger URL>
FLOW2_URL=<Power Automate Flow 2 HTTP trigger URL>
ANTHROPIC_API_KEY=<your-anthropic-api-key>
```
