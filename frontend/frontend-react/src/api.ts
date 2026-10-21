const AUTH_URL = import.meta.env.VITE_AUTH_URL || "http://localhost:8001";
const PAYMENT_URL = import.meta.env.VITE_PAYMENT_URL || "http://localhost:8000";
export interface Payment {
  id: string;
  amount: number;
  currency: string;
  status: string;
  created_at: string;
}

async function parseResponse(
  response: Response,
  unauthorizedMessage = "Session expirée ou accès non autorisé."
) {
  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      throw new Error(unauthorizedMessage);
    }

    throw new Error(`Erreur API : ${response.status}`);
  }

  return response.json();
}

export async function login(email: string, password: string): Promise<string> {
  const response = await fetch(`${AUTH_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await parseResponse(
    response,
    "Adresse e-mail ou mot de passe incorrect."
  );
  return data.access_token;
}

export async function getPayments(token: string): Promise<Payment[]> {
  const response = await fetch(`${PAYMENT_URL}/payments`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return parseResponse(response);
}

export async function createPayment(
  token: string,
  amount: number,
  currency: string
): Promise<Payment> {
  const response = await fetch(`${PAYMENT_URL}/payments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ amount, currency }),
  });

  return parseResponse(response);
}

export interface PaymentAnomaly {
  id: string;
  payment_id: string;
  is_anomaly: boolean | null;
  score: number | null;
  severity: string;
  model: string | null;
  analyzed_at: string;
}

export async function getPaymentAnomalies(
  token: string
): Promise<PaymentAnomaly[]> {
  const response = await fetch(
    `${PAYMENT_URL}/payments/anomalies?limit=100`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return parseResponse(response);
}