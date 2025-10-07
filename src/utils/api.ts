import type { UploadResponse, QueryResponse, HealthResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

export const api = {
  async checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE_URL}/health`);
    console.log('Health check response:', response);
    if (!response.ok) {
      throw new APIError(response.status, 'Failed to connect to backend');
    }
    return response.json();
  },

  async uploadPDF(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload_pdf`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Upload failed' }));
      throw new APIError(response.status, error.message || 'Failed to upload PDF');
    }

    return response.json();
  },

  async query(doc_id: string, query: string): Promise<QueryResponse> {
    const response = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ doc_id, query }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Query failed' }));
      throw new APIError(response.status, error.message || 'Failed to process query');
    }

    return response.json();
  },

  async listDocuments(): Promise<Array<{ doc_id: string; filename: string }>> {
    const response = await fetch(`${API_BASE_URL}/documents`);
    if (!response.ok) {
      throw new APIError(response.status, 'Failed to fetch documents');
    }
    return response.json();
  },
};
