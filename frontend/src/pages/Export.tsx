import { downloadExport } from "../api/client";

interface Props {
  userId: number;
}

export default function Export({ userId }: Props) {
  return (
    <div>
      <h2 className="text-xl font-bold text-gray-900 mb-4">Export Transactions</h2>
      <p className="text-sm text-gray-600 mb-6">
        Download all your transactions as a CSV file in Finagle's native format.
        This file can be re-imported later.
      </p>
      <button
        onClick={() => downloadExport(userId, "csv")}
        className="inline-block px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700"
      >
        Download CSV
      </button>
    </div>
  );
}
