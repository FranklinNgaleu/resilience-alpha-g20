
import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  ShieldAlert,
  WifiOff,
} from "lucide-react";
import { getPaymentAnomalies, type PaymentAnomaly } from "../api";

interface Props {
  token: string;
}

type Filter = "all" | "suspicious" | "unavailable";

export default function AnomalyMonitor({ token }: Props) {
  const [analyses, setAnalyses] = useState<PaymentAnomaly[]>([]);
  const [filter, setFilter] = useState<Filter>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const data = await getPaymentAnomalies(token);
      setAnalyses(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Impossible de récupérer les analyses IA."
      );
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const suspicious = analyses.filter(
    (a) => a.is_anomaly === true
  ).length;

  const unavailable = analyses.filter(
    (a) => a.is_anomaly === null
  ).length;

  const visible = analyses.filter((a) => {
    if (filter === "suspicious") return a.is_anomaly === true;
    if (filter === "unavailable") return a.is_anomaly === null;
    return true;
  });

  function statusBadge(value: boolean | null) {
    if (value === true) {
      return (
        <span className="rounded-full bg-red-500/15 px-3 py-1 text-xs font-medium text-red-400">
          Suspect
        </span>
      );
    }

    if (value === null) {
      return (
        <span className="rounded-full bg-amber-500/15 px-3 py-1 text-xs font-medium text-amber-400">
          Non analysé
        </span>
      );
    }

    return (
      <span className="rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-medium text-emerald-400">
        Normal
      </span>
    );
  }

  return (
    <div className="space-y-7">
      <div className="grid gap-5 sm:grid-cols-3">
        {[
          {
            label: "Analyses IA",
            value: analyses.length,
            icon: Activity,
            color: "text-blue-400",
          },
          {
            label: "Transactions suspectes",
            value: suspicious,
            icon: ShieldAlert,
            color: "text-red-400",
          },
          {
            label: "Analyses indisponibles",
            value: unavailable,
            icon: WifiOff,
            color: "text-amber-400",
          },
        ].map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.label}
              className="rounded-2xl border border-slate-800 bg-[#111c30] p-6"
            >
              <Icon size={27} className={`mb-4 ${stat.color}`} />
              <p className="text-sm text-slate-400">{stat.label}</p>
              <p className="mt-2 text-3xl font-bold">{stat.value}</p>
            </div>
          );
        })}
      </div>

      {suspicious > 0 && (
        <div
          role="alert"
          className="flex items-start gap-3 rounded-xl border border-red-800 bg-red-950/30 p-4 text-red-300"
        >
          <AlertTriangle className="mt-0.5 shrink-0" size={20} />
          <p>
            {suspicious} transaction(s) signalée(s) comme suspecte(s)
            par Isolation Forest. Une vérification est recommandée.
          </p>
        </div>
      )}

      <section className="rounded-2xl border border-slate-800 bg-[#111c30] p-6">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold">Historique des analyses IA</h3>
            <p className="mt-1 text-sm text-slate-400">
              Détection des anomalies par Isolation Forest
            </p>
          </div>

          <button
            type="button"
            onClick={() => void refresh()}
            disabled={loading}
            className="flex items-center gap-2 text-sm text-blue-400 disabled:opacity-50"
          >
            <RefreshCw size={17} className={loading ? "animate-spin" : ""} />
            Actualiser
          </button>
        </div>

        <div className="mb-6 flex flex-wrap gap-2">
          {[
            { id: "all", label: "Toutes" },
            { id: "suspicious", label: "Suspectes" },
            { id: "unavailable", label: "Non analysées" },
          ].map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setFilter(item.id as Filter)}
              className={`rounded-lg px-4 py-2 text-sm transition ${
                filter === item.id
                  ? "bg-blue-600 text-white"
                  : "bg-slate-800 text-slate-400 hover:text-white"
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>

        {error && (
          <p role="alert" className="mb-5 text-sm text-red-400">
            {error}
          </p>
        )}

        {loading ? (
          <p className="text-slate-400">Chargement des analyses...</p>
        ) : visible.length === 0 ? (
          <div className="py-10 text-center text-slate-400">
            <CheckCircle2 className="mx-auto mb-3 text-slate-500" size={30} />
            Aucune analyse pour ce filtre.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-700 text-slate-400">
                <tr>
                  <th className="pb-4 pr-4">Paiement</th>
                  <th className="pb-4 pr-4">Statut IA</th>
                  <th className="pb-4 pr-4">Score</th>
                  <th className="pb-4 pr-4">Gravité</th>
                  <th className="pb-4 pr-4">Modèle</th>
                  <th className="pb-4">Date</th>
                </tr>
              </thead>
              <tbody>
                {visible.map((analysis) => (
                  <tr
                    key={analysis.id}
                    className="border-b border-slate-800"
                  >
                    <td className="py-4 pr-4 font-mono text-xs">
                      {analysis.payment_id.slice(0, 8)}...
                    </td>
                    <td className="py-4 pr-4">
                      {statusBadge(analysis.is_anomaly)}
                    </td>
                    <td className="py-4 pr-4 font-mono">
                      {analysis.score === null
                        ? "—"
                        : analysis.score.toFixed(4)}
                    </td>
                    <td className="py-4 pr-4">
                      <span
                        className={
                          analysis.severity === "high"
                            ? "font-semibold text-red-400"
                            : analysis.severity === "medium"
                            ? "text-amber-400"
                            : "text-slate-300"
                        }
                      >
                        {analysis.severity}
                      </span>
                    </td>
                    <td className="py-4 pr-4 text-slate-400">
                      {analysis.model ?? "—"}
                    </td>
                    <td className="py-4 text-slate-400">
                      {new Date(analysis.analyzed_at).toLocaleString("fr-FR")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
