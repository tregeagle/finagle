import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { deleteUser } from "../api/client";

interface Props {
  userId: number;
  onDeleted: () => void;
}

export default function Settings({ userId, onDeleted }: Props) {
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleDelete() {
    setError("");
    try {
      await deleteUser(userId);
      onDeleted();
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-900 mb-6">Settings</h2>

      <div className="border border-red-200 rounded-lg p-6 bg-red-50">
        <h3 className="text-lg font-semibold text-red-900 mb-2">Danger Zone</h3>
        <p className="text-sm text-red-700 mb-4">
          Deleting your account will permanently remove all your data including
          transactions, and cannot be undone.
        </p>

        {error && (
          <div className="mb-4 p-3 bg-red-100 rounded text-sm text-red-800">
            {error}
          </div>
        )}

        {!confirming ? (
          <button
            onClick={() => setConfirming(true)}
            className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700"
          >
            Delete Account
          </button>
        ) : (
          <div className="flex items-center gap-3">
            <span className="text-sm text-red-800 font-medium">
              Are you sure? This cannot be undone.
            </span>
            <button
              onClick={handleDelete}
              className="px-4 py-2 bg-red-700 text-white text-sm font-medium rounded hover:bg-red-800"
            >
              Yes, delete everything
            </button>
            <button
              onClick={() => setConfirming(false)}
              className="px-4 py-2 bg-white text-gray-700 text-sm font-medium rounded border border-gray-300 hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
