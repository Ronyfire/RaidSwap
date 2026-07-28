import { useContext } from "react";
import { AuthContext } from "./auth-context";

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext debe usarse dentro de <AuthProvider>");
  }
  return context;
}
