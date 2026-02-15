import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createUser, type User } from "../api/client";

interface Props {
  user: User | null;
  setUser: (u: User) => void;
}

export default function Home({ user, setUser }: Props) {
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!username.trim()) return;
    setError("");
    setLoading(true);
    try {
      const u = await createUser(username.trim());
      setUser(u);
      navigate("/transactions");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to sign in");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Finagle</h1>
        <p className="text-gray-600 mb-6">
          Personal finance & CGT tracker. Enter your username to sign in or
          create a new account.
        </p>

        {user && (
          <div className="mb-6 p-3 bg-blue-50 rounded text-sm text-blue-700">
            Logged in as <strong>{user.username}</strong>.{" "}
            <button
              onClick={() => navigate("/transactions")}
              className="underline"
            >
              Continue
            </button>
          </div>
        )}

        {error && (
          <div className="mb-4 p-3 bg-red-50 rounded text-sm text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Username
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              Sign in
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-2">
            If the username doesn't exist, a new account will be created.
          </p>
        </form>
      </div>
    </div>
  );
}
