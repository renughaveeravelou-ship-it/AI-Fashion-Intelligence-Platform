import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Search } from "lucide-react";
import PinterestGrid from "../components/PinterestGrid";
import { api, FashionItem } from "../lib/api";

const CATEGORIES = ["All", "Shirts_&_Tops", "Dresses", "Pants", "Shoes", "Unknown"];

export default function Discover() {
  const [items, setItems] = useState<FashionItem[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.feed(48).then((r) => setItems(r.items)).catch(() => {});
  }, []);

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const r = await api.searchText(query, category);
      setItems(r.items);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <h1 className="text-3xl font-bold mb-2 shimmer-text">Discover</h1>
      <p className="text-zinc-400 mb-6">Pinterest-style fashion grid</p>

      <div className="glass rounded-2xl p-4 flex flex-col sm:flex-row gap-3 mb-8">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && search()}
            placeholder="Search styles…"
            className="w-full pl-10 pr-4 py-3 rounded-xl bg-black/30 border border-white/10 outline-none focus:border-[var(--color-primary)]"
          />
        </div>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="rounded-xl bg-black/30 border border-white/10 px-4 py-3"
        >
          {CATEGORIES.map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>
        <button
          onClick={search}
          disabled={loading}
          className="px-6 py-3 rounded-xl font-semibold text-white"
          style={{ background: "var(--color-primary)" }}
        >
          {loading ? "Searching…" : "Search"}
        </button>
      </div>

      <PinterestGrid items={items} />
    </motion.div>
  );
}
