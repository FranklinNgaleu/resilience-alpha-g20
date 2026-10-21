
import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  RefreshCw,
  ShieldCheck,
  CreditCard,
  AlertTriangle,
  CheckCircle2,
  LoaderCircle,
} from "lucide-react";

type ServiceStatus = "online" | "offline" | "checking";

interface Service {
  name: string;
  description: string;
  url: string;
  status: ServiceStatus;
  latency: number | null;
}

const initialServices: Service[] = [
  {
    name: "Auth Service",
    description: "Authentification JWT",
    url: "http://localhost:8001/health",
    status: "checking",
    latency: null,
  },
  {
    name: "Payment Service",
    description: "API de gestion des paiements",
    url: "http://localhost:8000/health",
    status: "checking",
    latency: null,
  },
];

async function checkService(service: Service): Promise<Service> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 4000);
  const start = performance.now();

  try {
    const response = await fetch(service.url, {
      signal: controller.signal,
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error("Service unavailable");
    }

    const data = await response.json();

    if (data.status !== "ok") {
      throw new Error("Unhealthy service");
    }

    return {
      ...service,
      status: "online",
      latency: Math.round(performance.now() - start),
    };
  } catch {
    return {
      ...service,
      status: "offline",
      latency: null,
    };
  } finally {
    clearTimeout(timeout);
  }
}

export default function SystemMonitor() {
  const [services, setServices] = useState(initialServices);
  const [refreshing, setRefreshing] = useState(false);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  const refresh = useCallback(async () => {
    setRefreshing(true);

    try {
      const results = await Promise.all(
        initialServices.map(checkService)
      );

      setServices(results);
      setLastCheck(new Date());
    } finally {
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void refresh();

    const interval = setInterval(() => {
      void refresh();
    }, 10000);

    return () => clearInterval(interval);
  }, [refresh]);

  const allOnline = services.every(
    (service) => service.status === "online"
  );

  const hasOffline = services.some(
    (service) => service.status === "offline"
  );

  return (
    <section className="rounded-2xl border border-slate-800 bg-[#111c30] p-6">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="flex items-center gap-2 text-lg font-semibold">
            <Activity className="text-blue-400" size={21} />
            Supervision des microservices
          </h3>

          <p className="mt-2 text-sm text-slate-400">
            Vérification automatique toutes les 10 secondes
          </p>
        </div>

        <button
          onClick={() => void refresh()}
          disabled={refreshing}
          className="flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 disabled:opacity-50"
        >
          <RefreshCw
            size={16}
            className={refreshing ? "animate-spin" : ""}
          />
          Actualiser
        </button>
      </div>

      <div className="mb-6 grid gap-4 md:grid-cols-2">
        {services.map((service, index) => {
          const Icon = index === 0 ? ShieldCheck : CreditCard;

          return (
            <div
              key={service.name}
              className="rounded-xl border border-slate-700/70 bg-[#0b1425] p-5"
            >
              <div className="mb-4 flex items-center justify-between">
                <Icon className="text-blue-400" size={26} />

                <span
                  className={`rounded-full px-3 py-1 text-xs ${
                    service.status === "online"
                      ? "bg-emerald-500/15 text-emerald-400"
                      : service.status === "offline"
                      ? "bg-red-500/15 text-red-400"
                      : "bg-slate-700 text-slate-300"
                  }`}
                >
                  {service.status === "online"
                    ? "En ligne"
                    : service.status === "offline"
                    ? "Hors ligne"
                    : "Vérification"}
                </span>
              </div>

              <h4 className="font-semibold">{service.name}</h4>
              <p className="mt-1 text-sm text-slate-400">
                {service.description}
              </p>

              <p className="mt-4 text-xs text-slate-500">
                Temps de réponse :{" "}
                {service.latency !== null
                  ? `${service.latency} ms`
                  : "Indisponible"}
              </p>
            </div>
          );
        })}
      </div>

      <div
        className={`flex items-center gap-3 rounded-xl border p-4 ${
          allOnline
            ? "border-emerald-800 bg-emerald-950/30"
            : hasOffline
            ? "border-red-800 bg-red-950/30"
            : "border-slate-700 bg-slate-800/40"
        }`}
      >
        {allOnline ? (
          <CheckCircle2 className="text-emerald-400" />
        ) : hasOffline ? (
          <AlertTriangle className="text-red-400" />
        ) : (
          <LoaderCircle className="animate-spin text-slate-400" />
        )}

        <div>
          <p className="font-medium">
            {allOnline
              ? "Tous les services surveillés sont opérationnels"
              : hasOffline
              ? "Incident détecté : un service est indisponible"
              : "Vérification en cours"}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            {lastCheck
              ? `Dernière vérification : ${lastCheck.toLocaleTimeString("fr-FR")}`
              : "En attente de la première vérification"}
          </p>
        </div>
      </div>
    </section>
  );
}
