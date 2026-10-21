import { useState, type FormEvent } from "react";
import {
  ShieldCheck,
  Mail,
  LockKeyhole,
  ArrowRight,
  LoaderCircle,
} from "lucide-react";
import { login } from "./api";
import Dashboard from "./components/Dashboard";

export default function App() {
  const [email, setEmail] = useState("demo@resilience.local");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const accessToken = await login(email, password);
      setToken(accessToken);
      setPassword("");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Impossible de se connecter."
      );
    } finally {
      setLoading(false);
    }
  }

  if (token) {
    return (
      <Dashboard
        token={token}
        onLogout={() => setToken(null)}
      />
    );
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#080f1f] px-5 py-12">
      <div className="pointer-events-none absolute -left-40 -top-40 h-96 w-96 rounded-full bg-blue-700/15 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-40 -right-32 h-96 w-96 rounded-full bg-indigo-700/20 blur-3xl" />

      <div className="relative w-full max-w-md">
        <div className="mb-9 text-center">
          <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl border border-blue-400/30 bg-blue-600/20">
            <ShieldCheck className="h-9 w-9 text-blue-400" />
          </div>

          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            RESILIENCE-ALPHA
          </h1>

          <p className="mt-3 text-sm text-slate-400">
            Plateforme sécurisée de gestion des paiements
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-slate-700/60 bg-[#111c30] p-8 shadow-2xl"
        >
          <h2 className="text-xl font-semibold text-white">
            Connexion
          </h2>
          <p className="mb-7 mt-2 text-sm text-slate-400">
            Accédez à votre espace de gestion.
          </p>

          <label
            htmlFor="email"
            className="mb-2 block text-sm font-medium text-slate-300"
          >
            Adresse e-mail
          </label>

          <div className="relative mb-5">
            <Mail
              size={19}
              className="absolute left-4 top-3.5 text-slate-500"
            />
            <input
              id="email"
              type="email"
              required
              autoComplete="username"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-[#0b1425] py-3 pl-12 pr-4 text-white outline-none transition focus:border-blue-500"
            />
          </div>

          <label
            htmlFor="password"
            className="mb-2 block text-sm font-medium text-slate-300"
          >
            Mot de passe
          </label>

          <div className="relative mb-6">
            <LockKeyhole
              size={19}
              className="absolute left-4 top-3.5 text-slate-500"
            />
            <input
              id="password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Votre mot de passe"
              className="w-full rounded-xl border border-slate-700 bg-[#0b1425] py-3 pl-12 pr-4 text-white outline-none transition focus:border-blue-500"
            />
          </div>

          {error && (
            <p role="alert" className="mb-5 text-sm text-red-400">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 py-3.5 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? (
              <LoaderCircle className="h-5 w-5 animate-spin" />
            ) : (
              <>
                Se connecter
                <ArrowRight size={19} />
              </>
            )}
          </button>
        </form>

        <div className="mt-7 flex items-center justify-center gap-2 text-xs text-slate-500">
          <ShieldCheck size={15} />
          Cyber-résilience · Microservices · Paiements sécurisés
        </div>
      </div>
    </main>
  );
}
