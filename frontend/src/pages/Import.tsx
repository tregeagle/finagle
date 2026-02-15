import { useState, useRef } from "react";
import { importCSV, getImportTemplateURL, type ImportResult } from "../api/client";

interface Props {
  userId: number;
}

export default function Import({ userId }: Props) {
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const res = await importCSV(userId, file);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed");
    } finally {
      setLoading(false);
    }
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }

  function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-900 mb-4">Import Transactions</h2>

      <div className="mb-4">
        <a
          href={getImportTemplateURL()}
          className="text-blue-600 hover:underline text-sm"
        >
          Download CSV template
        </a>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 rounded text-sm text-red-700">
          {error}
        </div>
      )}

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
          dragOver
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 hover:border-gray-400"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx"
          onChange={onChange}
          className="hidden"
        />
        {loading ? (
          <p className="text-gray-500">Importing...</p>
        ) : (
          <>
            <p className="text-gray-600 font-medium">
              Drop a file here or click to browse
            </p>
            <p className="text-gray-400 text-sm mt-1">
              Accepts .csv or .xlsx files (Finagle, Sharesight, Pearler)
            </p>
          </>
        )}
      </div>

      {result && (
        <div className="mt-6 p-4 bg-white rounded border border-gray-200">
          <h3 className="font-medium text-gray-900 mb-2">Import Results</h3>
          <p className="text-sm text-green-700">
            {result.imported} transaction{result.imported !== 1 ? "s" : ""}{" "}
            imported successfully.
          </p>
          {result.errors.length > 0 && (
            <div className="mt-2">
              <p className="text-sm text-red-700 font-medium">
                {result.errors.length} error{result.errors.length !== 1 ? "s" : ""}:
              </p>
              <ul className="mt-1 text-sm text-red-600 list-disc list-inside">
                {result.errors.map((err, i) => (
                  <li key={i}>{err}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
