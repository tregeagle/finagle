import { NavLink, Outlet, useNavigate } from "react-router-dom";
import type { User } from "../api/client";

interface Props {
  user: User | null;
  onLogout: () => void;
}

export default function Layout({ user, onLogout }: Props) {
  const navigate = useNavigate();

  function handleLogout() {
    onLogout();
    navigate("/");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200">
        <div className="mx-auto max-w-5xl px-4 flex items-center justify-between h-14">
          <div className="flex items-center gap-6">
            <NavLink to="/" className="text-lg font-bold text-gray-900">
              Finagle
            </NavLink>
            <NavLink
              to="/transactions"
              className={({ isActive }) =>
                `text-sm font-medium ${isActive ? "text-blue-600" : "text-gray-600 hover:text-gray-900"}`
              }
            >
              Transactions
            </NavLink>
            <NavLink
              to="/import"
              className={({ isActive }) =>
                `text-sm font-medium ${isActive ? "text-blue-600" : "text-gray-600 hover:text-gray-900"}`
              }
            >
              Import
            </NavLink>
            <NavLink
              to="/export"
              className={({ isActive }) =>
                `text-sm font-medium ${isActive ? "text-blue-600" : "text-gray-600 hover:text-gray-900"}`
              }
            >
              Export
            </NavLink>
            <NavLink
              to="/reports"
              className={({ isActive }) =>
                `text-sm font-medium ${isActive ? "text-blue-600" : "text-gray-600 hover:text-gray-900"}`
              }
            >
              Reports
            </NavLink>
            <NavLink
              to="/settings"
              className={({ isActive }) =>
                `text-sm font-medium ${isActive ? "text-red-600" : "text-gray-600 hover:text-gray-900"}`
              }
            >
              Settings
            </NavLink>
          </div>
          {user && (
            <div className="flex items-center gap-3 text-sm">
              <span className="text-gray-600">{user.username}</span>
              <button
                onClick={handleLogout}
                className="text-gray-500 hover:text-gray-700"
              >
                Switch user
              </button>
            </div>
          )}
        </div>
      </nav>
      <main className="mx-auto max-w-5xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
