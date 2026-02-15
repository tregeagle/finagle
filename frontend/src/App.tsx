import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState } from "react";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Transactions from "./pages/Transactions";
import Import from "./pages/Import";
import Export from "./pages/Export";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import type { User } from "./api/client";

export default function App() {
  const [user, setUser] = useState<User | null>(null);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home user={user} setUser={setUser} />} />
        <Route element={<Layout user={user} onLogout={() => setUser(null)} />}>
          <Route
            path="/transactions"
            element={
              user ? (
                <Transactions userId={user.id} />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />
          <Route
            path="/import"
            element={
              user ? (
                <Import userId={user.id} />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />
          <Route
            path="/export"
            element={
              user ? (
                <Export userId={user.id} />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />
          <Route
            path="/reports"
            element={
              user ? (
                <Reports userId={user.id} />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />
          <Route
            path="/settings"
            element={
              user ? (
                <Settings userId={user.id} onDeleted={() => setUser(null)} />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
