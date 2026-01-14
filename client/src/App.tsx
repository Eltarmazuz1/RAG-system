import { useState, useRef, useEffect } from 'react'
import { ChatService } from './ChatService'
import { ChatMessage } from './types'
import './App.css'

// Simple uuid generator
const generateUUID = () => crypto.randomUUID();

function App() {
    const [sessionId] = useState(generateUUID());
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<string>('');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setIsUploading(true);
        setUploadStatus(`Uploading ${file.name}...`);
        try {
            const res = await ChatService.uploadFile(file);
            setUploadStatus(`Uploaded! (${res.num_chunks} chunks indexed)`);
            setMessages(prev => [...prev, { role: 'assistant', content: `Document "${file.name}" has been uploaded and indexed. You can now ask questions about it.` }]);
        } catch (err: any) {
            setUploadStatus(`Upload failed: ${err.message}`);
        } finally {
            setIsUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleSend = () => {
        if (!input.trim() || isStreaming) return;

        const userMsg: ChatMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsStreaming(true);

        // Add placeholder assistant message
        setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

        ChatService.streamAnswer(sessionId, input, (event) => {
            if (event.type === 'token') {
                setMessages(prev => {
                    const newMsgs = [...prev];
                    const lastMsg = newMsgs[newMsgs.length - 1];
                    if (lastMsg.role === 'assistant') {
                        lastMsg.content += event.content || '';
                    }
                    return newMsgs;
                });
            } else if (event.type === 'done') {
                setIsStreaming(false);
            } else if (event.type === 'error') {
                setMessages(prev => {
                    const newMsgs = [...prev];
                    const lastMsg = newMsgs[newMsgs.length - 1];
                    if (lastMsg.role === 'assistant') {
                        lastMsg.content = `\n[System Error: ${event.content}]`;
                    }
                    return newMsgs;
                });
                setIsStreaming(false);
            }
        });
    };

    return (
        <div className="container">
            <header>
                <div className="title-area">
                    <h1>Antigravity RAG Chat</h1>
                    <span className="dot" style={{ backgroundColor: isStreaming ? '#ff4b4b' : '#4bff4b' }}></span>
                </div>
                {uploadStatus && <span className="upload-status-top">{uploadStatus}</span>}
            </header>

            <div className="chat-window">
                {messages.length === 0 && (
                    <div className="welcome-msg">
                        <h2>Hello!</h2>
                        <p>I can help you analyze your documents. Please upload a file to start.</p>
                        <div className="features">
                            <span>✓ PDF, Text, Markdown</span>
                            <span>✓ Real-time streaming</span>
                            <span>✓ Semantic search</span>
                        </div>
                    </div>
                )}
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role}`}>
                        <div className="message-content">
                            {msg.role === 'assistant' ? (
                                <span style={{ whiteSpace: 'pre-wrap' }}>
                                    {msg.content || (isStreaming && idx === messages.length - 1 ? 'Thinking...' : '')}
                                </span>
                            ) : (
                                msg.content
                            )}
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            <div className="input-area-wrapper">
                <div className="input-area">
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileUpload}
                        style={{ display: 'none' }}
                        accept=".txt,.md,.pdf"
                    />
                    <button
                        className="attach-btn"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isUploading || isStreaming}
                        title="Upload Document"
                    >
                        {isUploading ? '...' : '+'}
                    </button>
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder={isUploading ? "Uploading file..." : "Ask a question about your documents..."}
                        disabled={isStreaming || isUploading}
                    />
                    <button className="send-btn" onClick={handleSend} disabled={isStreaming || !input.trim() || isUploading}>
                        {isStreaming ? '...' : 'Send'}
                    </button>
                </div>
            </div>
        </div>
    )
}

export default App
