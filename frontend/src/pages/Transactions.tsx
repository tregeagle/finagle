import { useEffect, useState, useCallback } from "react";
import {
  getTransactions,
  createTransaction,
  deleteTransaction,
  type Transaction,
  type TransactionCreate,
  type TransactionFilters,
  type Action,
} from "../api/client";

interface Props {
  userId: number;
}

const EMPTY_FORM: TransactionCreate = {
  date: new Date().toISOString().slice(0, 10),
  time: "00:00:00",
  action: "buy",
  ticker: "",
  quantity: 0,
  price: "0",
  value: "0",
  fee: "0",
};

export default function Transactions({ userId }: Props) {
  const [txns, setTxns] = useState<Transaction[]>([]);
  const [filters, setFilters] = useState<TransactionFilters>({});
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<TransactionCreate>({ ...EMPTY_FORM });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getTransactions(userId, filters);
      setTxns(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }, [userId, filters]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await createTransaction(userId, form);
      setForm({ ...EMPTY_FORM });
      setShowForm(false);
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create");
    }
  }

  async function handleDelete(txnId: number) {
    try {
      await deleteTransaction(userId, txnId);
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">Transactions</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700"
        >
          {showForm ? "Cancel" : "Add Transaction"}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 rounded text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-3 mb-4">
        <input
          type="text"
          placeholder="Filter by ticker"
          value={filters.ticker || ""}
          onChange={(e) =>
            setFilters((f) => ({ ...f, ticker: e.target.value || undefined }))
          }
          className="border border-gray-300 rounded px-3 py-1.5 text-sm w-32"
        />
        <select
          value={filters.action || ""}
          onChange={(e) =>
            setFilters((f) => ({
              ...f,
              action: (e.target.value as Action) || undefined,
            }))
          }
          className="border border-gray-300 rounded px-3 py-1.5 text-sm"
        >
          <option value="">All actions</option>
          <option value="buy">Buy</option>
          <option value="sell">Sell</option>
        </select>
        <input
          type="text"
          placeholder="FY (e.g. 2024-2025)"
          value={filters.fy || ""}
          onChange={(e) =>
            setFilters((f) => ({ ...f, fy: e.target.value || undefined }))
          }
          className="border border-gray-300 rounded px-3 py-1.5 text-sm w-40"
        />
      </div>

      {/* Add form */}
      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="mb-4 p-4 bg-white rounded border border-gray-200 grid grid-cols-2 gap-3"
        >
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Date
            </label>
            <input
              type="date"
              value={form.date}
              onChange={(e) => setForm({ ...form, date: e.target.value })}
              required
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Time
            </label>
            <input
              type="time"
              step="1"
              value={form.time}
              onChange={(e) =>
                setForm({ ...form, time: e.target.value || "00:00:00" })
              }
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Action
            </label>
            <select
              value={form.action}
              onChange={(e) =>
                setForm({ ...form, action: e.target.value as Action })
              }
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
            >
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Ticker
            </label>
            <input
              type="text"
              value={form.ticker}
              onChange={(e) => setForm({ ...form, ticker: e.target.value })}
              required
              placeholder="e.g. BHP"
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Quantity
            </label>
            <input
              type="number"
              value={form.quantity}
              onChange={(e) =>
                setForm({ ...form, quantity: parseInt(e.target.value, 10) || 0 })
              }
              required
              min={1}
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Price
            </label>
            <input
              type="text"
              value={form.price}
              onChange={(e) => setForm({ ...form, price: e.target.value })}
              required
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Value
            </label>
            <input
              type="text"
              value={form.value}
              onChange={(e) => setForm({ ...form, value: e.target.value })}
              required
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Fee
            </label>
            <input
              type="text"
              value={form.fee}
              onChange={(e) => setForm({ ...form, fee: e.target.value })}
              required
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
            />
          </div>
          <div className="col-span-2">
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700"
            >
              Save Transaction
            </button>
          </div>
        </form>
      )}

      {/* Table */}
      {loading ? (
        <p className="text-gray-500 text-sm">Loading...</p>
      ) : txns.length === 0 ? (
        <p className="text-gray-500 text-sm">
          No transactions yet. Add one or import a CSV.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b border-gray-200 text-left text-gray-600">
                <th className="py-2 pr-3 font-medium">Date</th>
                <th className="py-2 pr-3 font-medium">Time</th>
                <th className="py-2 pr-3 font-medium">Action</th>
                <th className="py-2 pr-3 font-medium">Ticker</th>
                <th className="py-2 pr-3 font-medium text-right">Qty</th>
                <th className="py-2 pr-3 font-medium text-right">Price</th>
                <th className="py-2 pr-3 font-medium text-right">Value</th>
                <th className="py-2 pr-3 font-medium text-right">Fee</th>
                <th className="py-2 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {txns.map((t) => (
                <tr
                  key={t.id}
                  className="border-b border-gray-100 hover:bg-gray-50"
                >
                  <td className="py-2 pr-3">{t.date}</td>
                  <td className="py-2 pr-3">{t.time}</td>
                  <td className="py-2 pr-3">
                    <span
                      className={
                        t.action === "buy" ? "text-green-700" : "text-red-700"
                      }
                    >
                      {t.action.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-2 pr-3 font-medium">{t.ticker}</td>
                  <td className="py-2 pr-3 text-right">{t.quantity}</td>
                  <td className="py-2 pr-3 text-right">${t.price}</td>
                  <td className="py-2 pr-3 text-right">${t.value}</td>
                  <td className="py-2 pr-3 text-right">${t.fee}</td>
                  <td className="py-2">
                    <button
                      onClick={() => handleDelete(t.id)}
                      className="text-red-500 hover:text-red-700 text-xs"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
