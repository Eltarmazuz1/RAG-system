import { ChatStreamEvent } from './types';

export class ChatService {
    private static readonly API_BASE = '/api'; // Proxy will handle localhost:8000

    static streamAnswer(sessionId: string, question: string, onEvent: (event: ChatStreamEvent) => void): () => void {
        const params = new URLSearchParams({ session_id: sessionId, question });
        const url = `${this.API_BASE}/chat/stream?${params.toString()}`;

        const controller = new AbortController();

        (async () => {
            try {
                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'X-API-TOKEN': 'my-dev-token', // Hardcoded for this demo
                        'Accept': 'text/event-stream',
                    },
                    signal: controller.signal,
                });

                if (!response.ok) {
                    onEvent({ type: 'error', content: `Error: ${response.status} ${response.statusText}` });
                    return;
                }

                if (!response.body) {
                    onEvent({ type: 'error', content: 'No response body' });
                    return;
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n\n');
                    buffer = lines.pop() || ''; // Keep incomplete data in buffer

                    for (const section of lines) {
                        const sectionLines = section.split('\n');
                        for (const line of sectionLines) {
                            const trimmed = line.trim();
                            if (trimmed.startsWith('data: ')) {
                                const dataStr = trimmed.slice(6);
                                try {
                                    const data = JSON.parse(dataStr);
                                    if (data.type === 'token') {
                                        onEvent({ type: 'token', content: data.content });
                                    } else if (data.type === 'done') {
                                        onEvent({ type: 'done' });
                                    } else if (data.type === 'error') {
                                        onEvent({ type: 'error', content: data.content });
                                    }
                                } catch (e) {
                                    console.error("Parse error", e);
                                }
                            }
                        }
                    }
                }
            } catch (err: any) {
                if (err.name === 'AbortError') return;
                onEvent({ type: 'error', content: err.message });
            }
        })();

        return () => controller.abort();
    }

    static async uploadFile(file: File): Promise<{ document_id: string; num_chunks: number }> {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.API_BASE}/files/upload`, {
            method: 'POST',
            headers: {
                'X-API-TOKEN': 'my-dev-token',
            },
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        return response.json();
    }
}
