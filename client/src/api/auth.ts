import { apiFetch } from "./client";

export interface AuthUser {
  id: number;
  email: string;
  tier: string;
}

export interface AuthResponse {
  access_token: string;
  user: AuthUser;
}

export function register(email: string, password: string): Promise<AuthResponse> {
  return apiFetch<AuthResponse>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function login(email: string, password: string): Promise<AuthResponse> {
  return apiFetch<AuthResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}
