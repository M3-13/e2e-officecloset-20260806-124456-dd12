const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

function getToken(): string | null {
  return localStorage.getItem("access_token");
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  isFormData?: boolean,
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers: Record<string, string> = {};

  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const options: RequestInit = {
    method,
    headers,
  };

  if (body !== undefined) {
    if (isFormData && body instanceof FormData) {
      options.body = body;
    } else {
      headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(body);
    }
  }

  const response = await fetch(url, options);

  if (response.status === 401) {
    localStorage.removeItem("access_token");
  }

  if (!response.ok) {
    const errorBody = await response.text();
    let detail = `HTTP ${response.status}`;
    try {
      const parsed = JSON.parse(errorBody);
      detail = parsed.detail || detail;
    } catch {
      if (errorBody) detail = errorBody;
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function get<T>(path: string): Promise<T> {
  return request<T>("GET", path);
}

export async function post<T>(path: string, body?: unknown, isFormData?: boolean): Promise<T> {
  return request<T>("POST", path, body, isFormData);
}

export async function put<T>(path: string, body?: unknown, isFormData?: boolean): Promise<T> {
  return request<T>("PUT", path, body, isFormData);
}

export async function del<T>(path: string): Promise<T> {
  return request<T>("DELETE", path);
}
