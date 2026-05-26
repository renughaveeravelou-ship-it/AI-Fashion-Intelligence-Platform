import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import PinterestGrid from "../components/PinterestGrid";
import { api, FashionItem } from "../lib/api";

const TABS = [
  { id: "advanced", label: "Advanced AI" },
  { id: "tryon", label: "Virtual Try-On" },
  { id: "chat", label: "Chatbot" },
  { id: "trends", label: "Trends" },
  { id: "attributes", label: "Attributes" },
  { id: "personal", label: "Personalized" },
  { id: "voice", label: "Voice" },
  { id: "caption", label: "Captioning" },
  { id: "multimodal", label: "Multi-Modal" },
  { id: "rating", label: "Rating" },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function AIStudio() {
  const [tab, setTab] = useState<TabId>("advanced");
  const [items, setItems] = useState<FashionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");
  const [chatLog, setChatLog] = useState<{ role: string; text: string }[]>([]);
  const [tryOnResult, setTryOnResult] = useState<string | null>(null);
  const [trends, setTrends] = useState<Record<string, unknown> | null>(null);
  const [rating, setRating] = useState<{ rating: number; label: string } | null>(null);
  const [caption, setCaption] = useState("");
  const [attrs, setAttrs] = useState<unknown[]>([]);
  const [text, setText] = useState("");
  const [category, setCategory] = useState("All");
  const [file, setFile] = useState<File | null>(null);
  const [file2, setFile2] = useState<File | null>(null);
  const [textWeight, setTextWeight] = useState(0.5);
  const [region, setRegion] = useState("torso");

  const run = async (fn: () => Promise<void>) => {
    setLoading(true);
    try {
      await fn();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <h1 className="text-3xl font-bold mb-2 shimmer-text">AI Studio</h1>
      <p className="text-zinc-400 mb-6">All 10 original AI features — preserved</p>

      <div className="flex gap-2 overflow-x-auto pb-4 mb-6 scrollbar-thin">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`shrink-0 px-4 py-2 rounded-full text-sm transition-all ${
              tab === t.id ? "text-white shadow-lg" : "glass text-zinc-400"
            }`}
            style={tab === t.id ? { background: "var(--color-primary)" } : {}}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="glass rounded-2xl p-6 mb-8">
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="mb-4 rounded-lg bg-black/30 border border-white/10 px-3 py-2 text-sm"
        >
          {["All", "Shirts_&_Tops", "Dresses", "Pants", "Shoes", "Unknown"].map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>

        <AnimatePresence mode="wait">
          <motion.div key={tab} initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }}>
            {tab === "advanced" && (
              <>
                <input placeholder="Optional style text" value={text} onChange={(e) => setText(e.target.value)} className="w-full mb-3 p-3 rounded-xl bg-black/30 border border-white/10" />
                <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} className="mb-3" />
                <button disabled={!file || loading} onClick={() => run(async () => { if (!file) return; const r = await api.advanced(file, text, category); setItems(r.items); setAttrs(r.attributes); })} className="btn-primary">Run ensemble</button>
              </>
            )}
            {tab === "tryon" && (
              <>
                <p className="text-sm text-zinc-500 mb-2">Person photo + garment image</p>
                <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} className="mb-2 block" />
                <input type="file" accept="image/*" onChange={(e) => setFile2(e.target.files?.[0] || null)} className="mb-2 block" />
                <select value={region} onChange={(e) => setRegion(e.target.value)} className="mb-3 rounded-lg bg-black/30 px-3 py-2">
                  <option value="torso">Torso</option><option value="lower">Lower</option><option value="full">Full</option>
                </select>
                <button disabled={!file || !file2 || loading} onClick={() => run(async () => { if (!file || !file2) return; const r = await api.tryOn(file, file2, region); setTryOnResult(`data:image/jpeg;base64,${r.image_base64}`); })} className="btn-primary">Generate try-on</button>
                {tryOnResult && <img src={tryOnResult} alt="Try-on" className="mt-4 rounded-xl max-w-md" />}
              </>
            )}
            {tab === "chat" && (
              <>
                <div className="max-h-48 overflow-y-auto mb-3 space-y-2">{chatLog.map((m, i) => <div key={i} className={`text-sm p-2 rounded-lg ${m.role === "user" ? "bg-white/10 ml-8" : "bg-[var(--color-primary)]/20 mr-8"}`}>{m.text}</div>)}</div>
                <input value={msg} onChange={(e) => setMsg(e.target.value)} placeholder="Ask your stylist…" className="w-full mb-3 p-3 rounded-xl bg-black/30 border border-white/10" />
                <button disabled={!msg || loading} onClick={() => run(async () => { const r = await api.chat(msg); setChatLog((l) => [...l, { role: "user", text: msg }, { role: "bot", text: r.reply }]); setItems(r.items); setMsg(""); })} className="btn-primary">Send</button>
              </>
            )}
            {tab === "trends" && (
              <button onClick={() => run(async () => setTrends(await api.trends()))} className="btn-primary">Analyze trends</button>
            )}
            {tab === "attributes" && (
              <>
                <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} className="mb-3" />
                <button disabled={!file || loading} onClick={() => run(async () => { if (!file) return; const r = await api.attributes(file); setAttrs(r.attributes); })} className="btn-primary">Detect attributes</button>
                {attrs.length > 0 && <pre className="mt-4 text-xs text-zinc-400 overflow-auto">{JSON.stringify(attrs, null, 2)}</pre>}
              </>
            )}
            {tab === "personal" && (
              <>
                <input value={text} onChange={(e) => setText(e.target.value)} placeholder="What are you looking for?" className="w-full mb-3 p-3 rounded-xl bg-black/30 border border-white/10" />
                <button disabled={!text || loading} onClick={() => run(async () => { const r = await api.personalized(text, true, category); setItems(r.items); })} className="btn-primary">Personalized search</button>
              </>
            )}
            {tab === "voice" && (
              <>
                <input type="file" accept="audio/*" onChange={(e) => setFile(e.target.files?.[0] || null)} className="mb-3" />
                <button disabled={!file || loading} onClick={() => run(async () => { if (!file) return; const r = await api.voice(file, category); if (r.transcript) setText(r.transcript); setItems(r.items); })} className="btn-primary">Voice search</button>
                {text && <p className="text-sm mt-2 text-zinc-400">Transcript: {text}</p>}
              </>
            )}
            {tab === "caption" && (
              <>
                <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} className="mb-3" />
                <button disabled={!file || loading} onClick={() => run(async () => { if (!file) return; const r = await api.caption(file); setCaption(r.caption); const s = await api.searchText(r.caption, category); setItems(s.items); })} className="btn-primary">Caption & search</button>
                {caption && <p className="mt-3 text-[var(--color-accent)]">{caption}</p>}
              </>
            )}
            {tab === "multimodal" && (
              <>
                <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Text query" className="w-full mb-3 p-3 rounded-xl bg-black/30 border border-white/10" />
                <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} className="mb-2" />
                <label className="text-sm text-zinc-500">Text weight: {textWeight}</label>
                <input type="range" min={0} max={1} step={0.1} value={textWeight} onChange={(e) => setTextWeight(+e.target.value)} className="w-full mb-3" />
                <button disabled={loading} onClick={() => run(async () => { const r = await api.multimodal(text, file, textWeight, category); setItems(r.items); })} className="btn-primary">Multi-modal search</button>
              </>
            )}
            {tab === "rating" && (
              <>
                <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} className="mb-3" />
                <button disabled={!file || loading} onClick={() => run(async () => { if (!file) return; setRating(await api.rate(file)); })} className="btn-primary">Rate outfit</button>
                {rating && (
                  <div className="mt-4">
                    <p className="text-4xl font-bold text-[var(--color-accent)]">{rating.rating}/10</p>
                    <p className="text-zinc-400">{rating.label}</p>
                  </div>
                )}
              </>
            )}
          </motion.div>
        </AnimatePresence>

        {trends && tab === "trends" && (
          <pre className="mt-4 text-xs text-zinc-400 overflow-auto">{JSON.stringify(trends, null, 2)}</pre>
        )}
      </div>

      {items.length > 0 && tab !== "tryon" && tab !== "trends" && tab !== "rating" && (
        <>
          <h3 className="font-semibold mb-4">Results</h3>
          <PinterestGrid items={items} />
        </>
      )}

      <style>{`.btn-primary { padding: 0.75rem 1.5rem; border-radius: 9999px; font-weight: 600; color: white; background: var(--color-primary); } .btn-primary:disabled { opacity: 0.5; }`}</style>
    </motion.div>
  );
}
