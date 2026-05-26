import { Link, Outlet, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Home,
  LayoutDashboard,
  Grid3X3,
  Scan,
  Box,
  Sparkles,
  LogIn,
  LogOut,
  Palette,
} from "lucide-react";
import { useAuth } from "../lib/auth";
import { useTheme } from "../lib/theme";

const nav = [
  { to: "/", icon: Home, label: "Home" },
  { to: "/discover", icon: Grid3X3, label: "Discover" },
  { to: "/scan", icon: Scan, label: "AI Scan" },
  { to: "/showcase", icon: Box, label: "3D" },
  { to: "/studio", icon: Sparkles, label: "AI Studio" },
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
];

export default function Layout() {
  const { pathname } = useLocation();
  const { user, logout } = useAuth();
  const { themes, theme, setThemeId } = useTheme();

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      <motion.aside
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className="glass md:w-64 md:min-h-screen p-4 flex md:flex-col gap-2 md:sticky md:top-0 z-50 overflow-x-auto md:overflow-visible"
      >
        <Link to="/" className="flex items-center gap-2 px-3 py-2 shrink-0">
          <span className="text-xl font-bold shimmer-text">Smart Stylist</span>
        </Link>

        <nav className="flex md:flex-col gap-1 flex-1">
          {nav.map(({ to, icon: Icon, label }) => (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm transition-all whitespace-nowrap ${
                pathname === to
                  ? "bg-[var(--color-primary)] text-white shadow-lg"
                  : "text-zinc-400 hover:text-white hover:bg-white/5"
              }`}
            >
              <Icon size={18} />
              {label}
            </Link>
          ))}
        </nav>

        <div className="px-3 py-2 shrink-0">
          <label className="flex items-center gap-2 text-xs text-zinc-500 mb-1">
            <Palette size={14} /> AI Theme
          </label>
          <select
            value={theme.id}
            onChange={(e) => setThemeId(e.target.value)}
            className="w-full min-w-[120px] rounded-lg bg-black/30 border border-white/10 px-2 py-2 text-sm"
          >
            {themes.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex md:flex-col gap-2 px-2 pb-2 md:pb-0">
          {user ? (
            <>
              <span className="text-xs text-zinc-500 px-2 truncate">Hi, {user.username}</span>
              <button
                onClick={logout}
                className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-zinc-400 hover:bg-white/5"
              >
                <LogOut size={16} /> Log out
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm bg-[var(--color-primary)] text-white"
            >
              <LogIn size={16} /> Sign in
            </Link>
          )}
        </div>
      </motion.aside>

      <main className="flex-1 p-4 md:p-8 max-w-[1600px] w-full mx-auto">
        <Outlet />
      </main>
    </div>
  );
}
