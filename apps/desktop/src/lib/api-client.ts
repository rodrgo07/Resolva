import { API_BASE_URL } from "./constants";

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: unknown
  ) {
    super(`API Error: ${status} ${statusText}`);
    this.name = "ApiError";
  }
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  public setToken(token: string | null) {
    this.token = token;
  }

  public getToken(): string | null {
    return this.token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const isGet = !options.method || options.method === "GET";
    const { headers: optionHeaders, ...restOptions } = options;
    
    const baseHeaders: Record<string, string> = {};
    if (!isGet) {
      baseHeaders["Content-Type"] = "application/json";
    }
    if (this.token) {
      baseHeaders["Authorization"] = `Bearer ${this.token}`;
    }

    const config: RequestInit = {
      ...restOptions,
      headers: {
        ...baseHeaders,
        ...(optionHeaders as Record<string, string>),
      },
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        let data: unknown;
        try {
          data = await response.json();
        } catch {
          // response body is not JSON
        }
        
        if (response.status === 401 && !endpoint.includes("/api/auth/login") && !endpoint.includes("/api/auth/unlock") && !endpoint.includes("/api/auth/register")) {
          // Disparar evento global de sessao expirada se logado
          window.dispatchEvent(new CustomEvent("resolva-session-expired"));
        }

        throw new ApiError(response.status, response.statusText, data);
      }

      if (response.status === 204) {
        return undefined as T;
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) throw error;

      // Network error or backend not available
      throw new ApiError(0, "Não foi possível conectar ao servidor. Verifique se o backend está rodando.");
    }
  }

  async get<T>(endpoint: string, params?: Record<string, string | number | boolean | undefined>): Promise<T> {
    let url = endpoint;
    if (params) {
      const searchParams = new URLSearchParams();
      for (const [key, value] of Object.entries(params)) {
        if (value !== undefined) {
          searchParams.append(key, String(value));
        }
      }
      const qs = searchParams.toString();
      if (qs) url += `?${qs}`;
    }
    return this.request<T>(url, { method: "GET" });
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }
}

export const api = new ApiClient(API_BASE_URL);
