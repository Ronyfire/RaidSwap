import { useState, type ReactNode } from "react";
import { login as apiLogin, register as apiRegister, type AuthUser } from "../api/auth";
import { setToken } from "../api/authToken";
import { AuthContext } from "./auth-context";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);

  async function login(email: string, password: string) {
    const result = await apiLogin(email, password);
    setToken(result.access_token);
    setUser(result.user);
  }

  async function register(email: string, password: string) {
    const result = await apiRegister(email, password);
    setToken(result.access_token);
    setUser(result.user);
  }

  function logout() {
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated: user !== null, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}
