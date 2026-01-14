export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatStreamEvent {
  type: 'token' | 'done' | 'error';
  content?: string;
}
