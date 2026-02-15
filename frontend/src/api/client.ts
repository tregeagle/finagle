const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
const API_KEY = import.meta.env.VITE_API_KEY || "";

function authHeaders(): Record<string, string> {
  const headers: Record<string, string> = {};
  if (API_KEY) headers["X-API-Key"] = API_KEY;
  return headers;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const merged: RequestInit = { ...init };
  merged.headers = { ...authHeaders(), ...(init?.headers as Record<string, string>) };
  const res = await fetch(`${BASE_URL}${path}`, merged);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

async function requestBlob(path: string): Promise<Blob> {
  const res = await fetch(`${BASE_URL}${path}`, { headers: authHeaders() });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status}: ${body}`);
  }
  return res.blob();
}

// --- Types ---

export interface User {
  id: number;
  username: string;
  created_at: string;
}

export type Action = "buy" | "sell";

export interface TransactionCreate {
  date: string;
  time: string;
  action: Action;
  ticker: string;
  quantity: number;
  price: string;
  value: string;
  fee: string;
  contract_note?: string | null;
}

export interface Transaction extends TransactionCreate {
  id: number;
  user_id: number;
}

export interface ImportResult {
  imported: number;
  errors: string[];
}

export interface LotMatch {
  ticker: string;
  sell_date: string;
  quantity: number;
  cost_base: string;
  proceeds: string;
  raw_gain: string;
  held_over_12_months: boolean;
  discount: string;
  net_gain: string;
}

export interface FinancialYearSummary {
  financial_year: string;
  total_gains: string;
  total_losses: string;
  discount_gains: string;
  non_discount_gains: string;
  discount_amount: string;
  net_capital_gain: string;
  lot_matches: LotMatch[];
}

export interface CGTOverview {
  financial_years: FinancialYearSummary[];
}

// --- API Functions ---

export function createUser(username: string) {
  return request<User>("/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
  });
}

export function getUser(userId: number) {
  return request<User>(`/users/${userId}`);
}

export interface TransactionFilters {
  ticker?: string;
  action?: Action;
  fy?: string;
}

export function getTransactions(userId: number, filters?: TransactionFilters) {
  const params = new URLSearchParams();
  if (filters?.ticker) params.set("ticker", filters.ticker);
  if (filters?.action) params.set("action", filters.action);
  if (filters?.fy) params.set("fy", filters.fy);
  const qs = params.toString();
  return request<Transaction[]>(
    `/users/${userId}/transactions${qs ? `?${qs}` : ""}`
  );
}

export function createTransaction(userId: number, data: TransactionCreate) {
  return request<Transaction>(`/users/${userId}/transactions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function deleteTransaction(userId: number, txnId: number) {
  return request<void>(`/users/${userId}/transactions/${txnId}`, {
    method: "DELETE",
  });
}

export function importCSV(userId: number, file: File) {
  const form = new FormData();
  form.append("file", file);
  return request<ImportResult>(`/users/${userId}/import`, {
    method: "POST",
    body: form,
  });
}

export function getCGTOverview(userId: number) {
  return request<CGTOverview>(`/users/${userId}/reports/cgt`);
}

export function getCGTReport(userId: number, fy: string) {
  return request<CGTOverview>(`/users/${userId}/reports/cgt/${fy}`);
}

export function deleteUser(userId: number) {
  return request<void>(`/users/${userId}`, { method: "DELETE" });
}

export async function downloadExport(userId: number, format: "json" | "csv" = "json") {
  const blob = await requestBlob(`/users/${userId}/export?format=${format}`);
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `transactions.${format}`;
  a.click();
  URL.revokeObjectURL(url);
}

export async function downloadImportTemplate() {
  const blob = await requestBlob("/import/template");
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "stock_transactions.csv";
  a.click();
  URL.revokeObjectURL(url);
}
