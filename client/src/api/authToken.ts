// In-memory only — never localStorage (XSS risk). This means a page refresh
// clears the session and requires logging in again; that's the accepted
// trade-off until there's a real refresh-token flow (httpOnly cookie, "nivel
// avanzado" — not built yet, no need for it with a single short-lived access
// token during the tester phase).
let token: string | null = null;

export function getToken(): string | null {
  return token;
}

export function setToken(newToken: string | null): void {
  token = newToken;
}
