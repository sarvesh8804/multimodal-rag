export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  context?: Array<{ page: number; text: string }>;
}

export interface Document {
  doc_id: string;
  filename: string;
  uploadedAt: Date;
}

export interface UploadResponse {
  status: string;
  message: string;
  doc_id: string;
}

export interface QueryResponse {
  answer: string;
  context: Array<{ page: number; text: string }>;
}

export interface HealthResponse {
  status: string;
  backend: string;
}

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
}
