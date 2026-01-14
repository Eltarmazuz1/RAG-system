# RAG Chat App (No-Docker Mode)

## Prerequisites
- **Node.js** & **npm** (for Frontend)
- **Python 3.10+** (for Backend)
- **OpenAI API Key** (or Anthropic/Gemini)

## 1. Backend Setup

1. **Navigate to server**:
   ```bash
   cd server
   ```
2. **Environment & Dependencies**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configuration**:
   - Ensure your `.env` file has `OPENAI_API_KEY=sk-...`
   - Make sure `VECTOR_DB_URL=...` is either empty or commented out (so it uses local mode).
4. **Run Server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   > The server will automatically create a folder `qdrant_local_storage`. **No Docker needed.**

## 2. Frontend Setup

1. **Navigate to client**:
   ```bash
   cd client
   ```
2. **Install & Run**:
   ```bash
   npm install
   npm run dev
   ```
   > Open: http://localhost:5173

## 3. How to Start Chatting

1. **Upload a file** (required for RAG to work):
   - Go to `http://localhost:8000/docs`
   - Use the `POST /api/files/upload` endpoint.
   - Click "Try it out", select a `.txt` file, and click "Execute".
   - **Note**: You must add the header `X-API-TOKEN: my-dev-token` (done automatically in Swagger if configured, or use curl).
2. **Talk to the Agent**:
   - Go to `http://localhost:5173`
   - Ask a question based on the document you uploaded.
