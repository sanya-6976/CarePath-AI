const BASE_URL = import.meta.env.VITE_API_URL || 'https://carepath-ai-production-508e.up.railway.app';

class ApiClient {
  private getHeaders(): HeadersInit {
    const token = localStorage.getItem('carepath_token');
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  async get<T>(path: string): Promise<T> {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    return this.handleResponse<T>(response);
  }

  async post<T>(path: string, body: any): Promise<T> {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(body),
    });
    return this.handleResponse<T>(response);
  }

  async postFile<T>(path: string, file: File, fieldName: string = 'file'): Promise<T> {
    const token = localStorage.getItem('carepath_token');
    const formData = new FormData();
    formData.append(fieldName, file);

    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers,
      body: formData,
    });
    return this.handleResponse<T>(response);
  }

  async uploadDocument<T>(path: string, file: File, category: string, patientId?: string): Promise<T> {
    const token = localStorage.getItem('carepath_token');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    if (patientId) {
      formData.append('patient_id', patientId);
    }

    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers,
      body: formData,
    });
    return this.handleResponse<T>(response);
  }

  async put<T>(path: string, body: any): Promise<T> {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(body),
    });
    return this.handleResponse<T>(response);
  }

  async delete<T>(path: string): Promise<T> {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    return this.handleResponse<T>(response);
  }

  private isExpiring = false;

  private async handleResponse<T>(response: Response): Promise<T> {
    if (response.status === 401) {
      if (!this.isExpiring) {
        this.isExpiring = true;
        localStorage.removeItem('carepath_token');
        localStorage.removeItem('carepath_patient_id');
        window.dispatchEvent(new Event('auth_expired'));
        setTimeout(() => {
          this.isExpiring = false;
        }, 5000);
      }
      throw new Error('Session expired. Please sign in again.');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      if (response.status >= 500) {
        throw new Error('CarePath is temporarily unavailable. Please try again in a moment.');
      }
      throw new Error(errorData.detail || errorData.message || `Request failed with status ${response.status}`);
    }

    const text = await response.text();
    return text ? (JSON.parse(text) as T) : ({} as T);
  }
}

export const apiClient = new ApiClient();
