import { useEffect, useState } from "react";
import {
  ShieldCheck, LayoutDashboard, CreditCard,
  History, LogOut, Plus, RefreshCw,
  CheckCircle2, Wallet, Activity
} from "lucide-react";
import { getPayments, createPayment, type Payment } from "../api";
import PaymentChart from "./PaymentChart";
import SystemMonitor from "./SystemMonitor";

interface DashboardProps {
  token: string;
  onLogout: () => void;
}

type Page = "dashboard" | "payment" | "history";

export default function Dashboard({ token, onLogout }: DashboardProps) {
  const [page, setPage] = useState<Page>("dashboard");
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState("EUR");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadPayments() {
    setLoading(true);
    setError("");

    try {
      const data = await getPayments(token);
      setPayments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur API");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadPayments();
  }, [token]);

  async function handlePayment(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    const value = Number(amount);

    if (!Number.isFinite(value) || value <= 0) {
      setError("Veuillez saisir un montant valide.");
      return;
    }

    setSubmitting(true);

    try {
      await createPayment(token, value, currency);
      setSuccess("Paiement effectué avec succès !");
      setAmount("");
      await loadPayments();
      setPage("dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Paiement impossible");
    } finally {
      setSubmitting(false);
    }
  }

  const total = payments
    .filter((p) => p.currency === "EUR")
    .reduce((sum, p) => sum + Number(p.amount), 0);

  const accepted = payments.filter((p) => p.status === "accepted").length;
  const successRate = payments.length
    ? Math.round((accepted / payments.length) * 100)
    : 0;

  const formatAmount = (value: number, code = "EUR") =>
    new Intl.NumberFormat("fr-FR", {
      style: "currency",
      currency: code,
    }).format(value);

  return (
    <div className="min-h-screen bg-[#080f1f] text-white md:flex">
      <aside className="w-full border-b border-slate-800 bg-[#0d1729] p-5 md:min-h-screen md:w-64 md:border-b-0 md:border-r">
        <div className="mb-10 flex items-center gap-3">
          <div className="rounded-xl bg-blue-600/20 p-2">
            <ShieldCheck className="text-blue-400" size={30} />
          </div>
          <div>
            <h1 className="text-sm font-bold">RESILIENCE-ALPHA</h1>
            <p className="text-xs text-slate-500">Secure Payments</p>
          </div>
        </div>

        <nav className="flex flex-wrap gap-2 md:flex-col">
          {[
            { id: "dashboard", label: "Tableau de bord", icon: LayoutDashboard },
            { id: "payment", label: "Nouveau paiement", icon: CreditCard },
            { id: "history", label: "Historique", icon: History },
          ].map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.id}
                onClick={() => {
                  setPage(item.id as Page);
                  setError("");
                  setSuccess("");
                }}
                className={`flex items-center gap-3 rounded-xl px-4 py-3 text-sm transition ${
                  page === item.id
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                }`}
              >
                <Icon size={18} />
                {item.label}
              </button>
            );
          })}
        </nav>

        <button
          onClick={onLogout}
          className="mt-10 flex items-center gap-3 px-4 py-3 text-sm text-red-400 hover:text-red-300"
        >
          <LogOut size={18} />
          Déconnexion
        </button>
      </aside>

      <main className="min-w-0 flex-1 p-6 md:p-10">
        <header className="mb-9 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="mb-2 text-sm text-slate-400">
              Plateforme de gestion sécurisée
            </p>
            <h2 className="text-3xl font-bold">
              {page === "dashboard"
                ? "Tableau de bord"
                : page === "payment"
                ? "Nouveau paiement"
                : "Historique des paiements"}
            </h2>
          </div>

          <button
            onClick={() => {
              setError("");
              setSuccess("");
              setPage("payment");
            }}
            className="flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold hover:bg-blue-500"
          >
            <Plus size={18} />
            Nouveau paiement
          </button>
        </header>

        {error && (
          <div role="alert" className="mb-6 rounded-xl border border-red-800 bg-red-950/40 p-4 text-red-300">
            {error}
          </div>
        )}

        {success && (
          <div role="status" className="mb-6 rounded-xl border border-emerald-800 bg-emerald-950/40 p-4 text-emerald-300">
            {success}
          </div>
        )}

        {page === "dashboard" && (
          <>
            <div className="mb-8 grid gap-5 lg:grid-cols-3">
              {[
                {
                  label: "Total paiements",
                  value: String(payments.length),
                  icon: CreditCard,
                  color: "text-blue-400",
                },
                {
                  label: "Volume EUR",
                  value: formatAmount(total),
                  icon: Wallet,
                  color: "text-emerald-400",
                },
                {
                  label: "Taux de réussite",
                  value: `${successRate} %`,
                  icon: CheckCircle2,
                  color: "text-violet-400",
                },
                
              ].map((stat) => {
                const Icon = stat.icon;

                return (
                  <div
                    key={stat.label}
                    className="rounded-2xl border border-slate-800 bg-[#111c30] p-6"
                  >
                    <Icon className={`mb-4 ${stat.color}`} size={27} />
                    <p className="text-sm text-slate-400">{stat.label}</p>
                    <p className="mt-2 text-3xl font-bold">{stat.value}</p>
                  </div>
                );
              })}
            </div>

            <div className="mb-8">
                <PaymentChart payments={payments} />
                </div>

                <div className="mb-8">
                <SystemMonitor />
            </div>

            <section className="rounded-2xl border border-slate-800 bg-[#111c30] p-6">
              <div className="mb-6 flex items-center justify-between">
                <h3 className="text-lg font-semibold">
                  Transactions récentes
                </h3>
                <button
                  onClick={() => void loadPayments()}
                  aria-label="Actualiser les paiements"
                  className="text-slate-400 hover:text-white"
                >
                  <RefreshCw size={19} />
                </button>
              </div>


              <PaymentTable payments={payments.slice(0, 5)} loading={loading} />
            </section>
           
          </>
        )}

        {page === "payment" && (
          <section className="max-w-xl rounded-2xl border border-slate-800 bg-[#111c30] p-7">
            <div className="mb-7 flex items-center gap-3">
              <Activity className="text-blue-400" />
              <h3 className="text-xl font-semibold">Effectuer un paiement</h3>
            </div>

            <form onSubmit={handlePayment}>
              <label className="mb-2 block text-sm text-slate-300">
                Montant
              </label>
              <input
                type="number"
                min="0.01"
                step="0.01"
                required
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="25.50"
                className="mb-5 w-full rounded-xl border border-slate-700 bg-[#0b1425] p-3 outline-none focus:border-blue-500"
              />

              <label className="mb-2 block text-sm text-slate-300">
                Devise
              </label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="mb-7 w-full rounded-xl border border-slate-700 bg-[#0b1425] p-3"
              >
                <option value="EUR">EUR — Euro</option>
                <option value="USD">USD — Dollar</option>
              </select>

              <button
                type="submit"
                disabled={submitting}
                className="w-full rounded-xl bg-blue-600 py-3 font-semibold hover:bg-blue-500 disabled:opacity-50"
              >
                {submitting ? "Traitement..." : "Confirmer le paiement"}
              </button>
            </form>
          </section>
        )}

        {page === "history" && (
          <section className="rounded-2xl border border-slate-800 bg-[#111c30] p-6">
            <div className="mb-6 flex items-center justify-between">
              <h3 className="text-lg font-semibold">Toutes les transactions</h3>
              <button
                onClick={() => void loadPayments()}
                className="flex items-center gap-2 text-sm text-blue-400"
              >
                <RefreshCw size={17} />
                Actualiser
              </button>
            </div>

            <PaymentTable payments={payments} loading={loading} />
          </section>
        )}
      </main>
    </div>
  );
}

function PaymentTable({
  payments,
  loading,
}: {
  payments: Payment[];
  loading: boolean;
}) {
  if (loading) {
    return <p className="text-slate-400">Chargement des paiements...</p>;
  }

  if (payments.length === 0) {
    return <p className="text-slate-400">Aucun paiement disponible.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-slate-700 text-slate-400">
          <tr>
            <th className="pb-4">Transaction</th>
            <th className="pb-4">Montant</th>
            <th className="pb-4">Statut</th>
            <th className="pb-4">Date</th>
          </tr>
        </thead>
        <tbody>
          {payments.map((payment) => (
            <tr key={payment.id} className="border-b border-slate-800">
              <td className="py-4 font-mono text-xs">
                {payment.id.slice(0, 8)}...
              </td>
              <td className="py-4">
                {new Intl.NumberFormat("fr-FR", {
                  style: "currency",
                  currency: payment.currency,
                }).format(Number(payment.amount))}
              </td>
              <td className="py-4">
                <span className="rounded-full bg-emerald-500/15 px-3 py-1 text-xs text-emerald-400">
                  {payment.status}
                </span>
              </td>
              <td className="py-4 text-slate-400">
                {new Date(payment.created_at).toLocaleString("fr-FR")}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
