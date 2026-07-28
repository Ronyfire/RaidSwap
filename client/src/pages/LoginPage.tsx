import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthContext } from "../context/useAuthContext";
import { ApiError } from "../api/client";

export function LoginPage() {
  const { login, register } = useAuthContext();
  const navigate = useNavigate();

  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, password);
      }
      navigate("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <form
        onSubmit={handleSubmit}
        className="w-[340px] bg-surface border border-border rounded-md p-6"
      >
        <div className="flex items-center gap-2 mb-6">
          <div className="w-2.5 h-2.5 bg-accent rotate-45" />
          <div className="font-heading font-bold text-lg tracking-wide">RAIDSWAP</div>
        </div>

        <label className="block text-[11px] uppercase tracking-wide text-text-subtle mb-1.5">
          Email
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full px-2.5 py-2 mb-3.5 bg-background border border-border-strong rounded text-text text-[13.5px]"
        />

        <label className="block text-[11px] uppercase tracking-wide text-text-subtle mb-1.5">
          Password
        </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="w-full px-2.5 py-2 mb-4 bg-background border border-border-strong rounded text-text text-[13.5px]"
        />

        {error && <p className="text-danger text-[12.5px] mb-3">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-accent border-none rounded px-3 py-2.5 text-accent-ink font-bold text-[13px] mb-3"
        >
          {mode === "login" ? "Log in" : "Create account"}
        </button>

        <button
          type="button"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
          className="w-full text-text-muted text-[12.5px]"
        >
          {mode === "login" ? "Need an account? Register" : "Already have an account? Log in"}
        </button>
      </form>
    </div>
  );
}
