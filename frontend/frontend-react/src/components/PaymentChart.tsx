
import { useMemo } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity } from "lucide-react";
import type { Payment } from "../api";

interface PaymentChartProps {
  payments: Payment[];
}

export default function PaymentChart({
  payments,
}: PaymentChartProps) {
  const data = useMemo(() => {
    const days = new Map<string, number>();

    // Les 7 derniers jours, aujourd'hui inclus
    for (let offset = 6; offset >= 0; offset--) {
      const date = new Date();
      date.setHours(0, 0, 0, 0);
      date.setDate(date.getDate() - offset);

      const key = [
        date.getFullYear(),
        String(date.getMonth() + 1).padStart(2, "0"),
        String(date.getDate()).padStart(2, "0"),
      ].join("-");

      days.set(key, 0);
    }

    for (const payment of payments) {
      if (payment.currency !== "EUR") continue;

      const date = new Date(payment.created_at);

      if (Number.isNaN(date.getTime())) continue;

      const key = [
        date.getFullYear(),
        String(date.getMonth() + 1).padStart(2, "0"),
        String(date.getDate()).padStart(2, "0"),
      ].join("-");

      if (days.has(key)) {
        days.set(
          key,
          (days.get(key) ?? 0) + Number(payment.amount)
        );
      }
    }

    return Array.from(days, ([date, amount]) => ({
      date,
      label: new Date(`${date}T12:00:00`).toLocaleDateString(
        "fr-FR",
        { day: "2-digit", month: "2-digit" }
      ),
      amount: Math.round(amount * 100) / 100,
    }));
  }, [payments]);

  const formatEUR = (value: number) =>
    new Intl.NumberFormat("fr-FR", {
      style: "currency",
      currency: "EUR",
    }).format(value);

  return (
    <section className="rounded-2xl border border-slate-800 bg-[#111c30] p-6">
      <div className="mb-7 flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Activity size={20} className="text-blue-400" />
            <h3 className="text-lg font-semibold text-white">
              Activité des paiements
            </h3>
          </div>

          <p className="mt-2 text-sm text-slate-400">
            Volume des paiements EUR sur les 7 derniers jours
          </p>
        </div>

        <span className="rounded-lg border border-slate-700 px-3 py-2 text-xs text-slate-400">
          7 derniers jours
        </span>
      </div>

      <div className="h-72 w-full min-w-0">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient
                id="paymentGradient"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop
                  offset="5%"
                  stopColor="#3b82f6"
                  stopOpacity={0.35}
                />
                <stop
                  offset="95%"
                  stopColor="#3b82f6"
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>

            <CartesianGrid
              stroke="#26354c"
              strokeDasharray="4 4"
              vertical={false}
            />

            <XAxis
              dataKey="label"
              stroke="#94a3b8"
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 12 }}
            />

            <YAxis
              stroke="#94a3b8"
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 12 }}
              width={55}
            />

            <Tooltip
              formatter={(value) =>
                formatEUR(Number(value ?? 0))
              }
              contentStyle={{
                backgroundColor: "#111c30",
                border: "1px solid #334155",
                borderRadius: "12px",
                color: "#ffffff",
              }}
              labelStyle={{ color: "#ffffff" }}
            />

            <Area
              type="monotone"
              dataKey="amount"
              name="Volume EUR"
              stroke="#3b82f6"
              strokeWidth={3}
              fill="url(#paymentGradient)"
              activeDot={{ r: 6 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <p className="mt-3 text-xs text-slate-500">
      </p>
    </section>
  );
}
