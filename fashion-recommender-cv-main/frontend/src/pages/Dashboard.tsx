import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BarChart3, Heart, Database, Sparkles } from "lucide-react";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    api.dashboard().then(setStats).catch(() => api.dashboard().then(setStats));
  }, []);

  const cards = [
    { icon: Database, label: "Catalog items", value: stats?.catalog_size ?? "—" },
    { icon: Heart, label: "Liked items", value: stats?.liked_count ?? 0 },
    { icon: Sparkles, label: "Style profile", value: stats?.profile_active ? "Active" : "Inactive" },
    { icon: BarChart3, label: "Season", value: stats?.current_season ?? "—" },
  ];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
      <p className="text-zinc-400 mb-8">
        {user ? `Welcome back, ${user.username}` : "Sign in to track your style profile"}
      </p>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        {cards.map(({ icon: Icon, label, value }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="glass rounded-2xl p-6"
          >
            <Icon className="text-[var(--color-primary)] mb-3" size={28} />
            <p className="text-2xl font-bold">{String(value)}</p>
            <p className="text-sm text-zinc-500">{label}</p>
          </motion.div>
        ))}
      </div>

      {Array.isArray(stats?.rising_categories) && (
        <div className="glass rounded-2xl p-6 mb-8">
          <h2 className="font-semibold mb-2">Rising categories</h2>
          <p className="text-zinc-300">{(stats.rising_categories as string[]).join(" · ")}</p>
        </div>
      )}

      <div className="glass rounded-2xl p-6">
        <h2 className="font-semibold mb-4">All AI features (preserved)</h2>
        <ul className="grid sm:grid-cols-2 gap-2 text-sm text-zinc-400">
          {(stats?.ai_features as string[] | undefined)?.map((f) => (
            <li key={f} className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-accent)]" />
              {f}
            </li>
          ))}
        </ul>
      </div>
    </motion.div>
  );
}
