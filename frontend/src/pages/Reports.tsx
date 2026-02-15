import { useEffect, useState } from "react";
import {
  getCGTOverview,
  getCGTReport,
  type CGTOverview,
  type FinancialYearSummary,
} from "../api/client";

interface Props {
  userId: number;
}

function fmt(value: string) {
  const n = parseFloat(value);
  if (isNaN(n)) return value;
  return n.toLocaleString("en-AU", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export default function Reports({ userId }: Props) {
  const [overview, setOverview] = useState<CGTOverview | null>(null);
  const [selectedFY, setSelectedFY] = useState<string>("");
  const [detail, setDetail] = useState<FinancialYearSummary | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getCGTOverview(userId)
      .then((data) => {
        setOverview(data);
        if (data.financial_years.length > 0) {
          setSelectedFY(data.financial_years[0].financial_year);
        }
      })
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Failed to load")
      )
      .finally(() => setLoading(false));
  }, [userId]);

  useEffect(() => {
    if (!selectedFY) {
      setDetail(null);
      return;
    }
    getCGTReport(userId, selectedFY)
      .then((data) => {
        const fy = data.financial_years.find(
          (f) => f.financial_year === selectedFY
        );
        setDetail(fy || null);
      })
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Failed to load report")
      );
  }, [userId, selectedFY]);

  if (loading) return <p className="text-gray-500 text-sm">Loading...</p>;

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-900 mb-4">CGT Reports</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-50 rounded text-sm text-red-700">
          {error}
        </div>
      )}

      {!overview || overview.financial_years.length === 0 ? (
        <p className="text-gray-500 text-sm">
          No CGT data yet. Add some sell transactions first.
        </p>
      ) : (
        <>
          {/* FY selector */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Financial Year
            </label>
            <select
              value={selectedFY}
              onChange={(e) => setSelectedFY(e.target.value)}
              className="border border-gray-300 rounded px-3 py-1.5 text-sm"
            >
              {overview.financial_years.map((fy) => (
                <option key={fy.financial_year} value={fy.financial_year}>
                  {fy.financial_year}
                </option>
              ))}
            </select>
          </div>

          {/* Summary cards */}
          {detail && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <Card label="Total Gains" value={`$${fmt(detail.total_gains)}`} />
                <Card
                  label="Total Losses"
                  value={`$${fmt(detail.total_losses)}`}
                  negative
                />
                <Card
                  label="Discount Amount"
                  value={`$${fmt(detail.discount_amount)}`}
                />
                <Card
                  label="Net Capital Gain"
                  value={`$${fmt(detail.net_capital_gain)}`}
                  highlight
                />
              </div>

              {/* Lot matches */}
              {detail.lot_matches.length > 0 && (
                <div className="overflow-x-auto">
                  <h3 className="font-medium text-gray-900 mb-2">
                    Lot Matches
                  </h3>
                  <table className="w-full text-sm border-collapse">
                    <thead>
                      <tr className="border-b border-gray-200 text-left text-gray-600">
                        <th className="py-2 pr-3 font-medium">Ticker</th>
                        <th className="py-2 pr-3 font-medium">Sell Date</th>
                        <th className="py-2 pr-3 font-medium text-right">
                          Qty
                        </th>
                        <th className="py-2 pr-3 font-medium text-right">
                          Cost Base
                        </th>
                        <th className="py-2 pr-3 font-medium text-right">
                          Proceeds
                        </th>
                        <th className="py-2 pr-3 font-medium text-right">
                          Raw Gain
                        </th>
                        <th className="py-2 pr-3 font-medium">Held 12m+</th>
                        <th className="py-2 pr-3 font-medium text-right">
                          Discount
                        </th>
                        <th className="py-2 font-medium text-right">
                          Net Gain
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.lot_matches.map((m, i) => (
                        <tr
                          key={i}
                          className="border-b border-gray-100 hover:bg-gray-50"
                        >
                          <td className="py-2 pr-3 font-medium">{m.ticker}</td>
                          <td className="py-2 pr-3">{m.sell_date}</td>
                          <td className="py-2 pr-3 text-right">{m.quantity}</td>
                          <td className="py-2 pr-3 text-right">
                            ${fmt(m.cost_base)}
                          </td>
                          <td className="py-2 pr-3 text-right">
                            ${fmt(m.proceeds)}
                          </td>
                          <td
                            className={`py-2 pr-3 text-right ${parseFloat(m.raw_gain) < 0 ? "text-red-600" : ""}`}
                          >
                            ${fmt(m.raw_gain)}
                          </td>
                          <td className="py-2 pr-3">
                            {m.held_over_12_months ? "Yes" : "No"}
                          </td>
                          <td className="py-2 pr-3 text-right">
                            ${fmt(m.discount)}
                          </td>
                          <td
                            className={`py-2 text-right ${parseFloat(m.net_gain) < 0 ? "text-red-600" : ""}`}
                          >
                            ${fmt(m.net_gain)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}

function Card({
  label,
  value,
  negative,
  highlight,
}: {
  label: string;
  value: string;
  negative?: boolean;
  highlight?: boolean;
}) {
  return (
    <div
      className={`p-4 rounded border ${highlight ? "bg-blue-50 border-blue-200" : "bg-white border-gray-200"}`}
    >
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p
        className={`text-lg font-semibold ${negative ? "text-red-600" : "text-gray-900"}`}
      >
        {value}
      </p>
    </div>
  );
}
