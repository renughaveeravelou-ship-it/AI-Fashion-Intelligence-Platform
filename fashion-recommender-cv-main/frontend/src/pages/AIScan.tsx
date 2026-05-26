import { useState } from "react";
import { motion } from "framer-motion";
import ScanOverlay from "../components/ScanOverlay";
import PinterestGrid from "../components/PinterestGrid";
import { api, FashionItem } from "../lib/api";

export default function AIScan() {
  const [preview, setPreview] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);
  const [items, setItems] = useState<FashionItem[]>([]);
  const [attrs, setAttrs] = useState<unknown[]>([]);

  const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPreview(URL.createObjectURL(file));
    setScanning(true);
    setItems([]);
    try {
      const [searchRes, attrRes] = await Promise.all([
        api.searchImage(file),
        api.attributes(file),
      ]);
      setItems(searchRes.items);
      setAttrs(attrRes.attributes);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Scan failed");
    } finally {
      setScanning(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <h1 className="text-3xl font-bold mb-2 shimmer-text">AI Scan</h1>
      <p className="text-zinc-400 mb-8">Upload an outfit — YOLO detects items & FashionCLIP finds matches</p>

      <div className="grid lg:grid-cols-2 gap-8">
        <div className="relative glass rounded-2xl p-6 min-h-[320px] flex flex-col items-center justify-center">
          {preview ? (
            <div className="relative w-full max-w-md">
              <img src={preview} alt="Scan" className="w-full rounded-xl" />
              <ScanOverlay active={scanning} />
            </div>
          ) : (
            <label className="cursor-pointer text-center">
              <input type="file" accept="image/*" className="hidden" onChange={onFile} />
              <div className="w-24 h-24 mx-auto mb-4 rounded-full border-2 border-dashed border-[var(--color-primary)] flex items-center justify-center text-4xl">
                📷
              </div>
              <p className="text-zinc-400">Tap to upload & scan</p>
            </label>
          )}
          {preview && !scanning && (
            <label className="mt-4 text-sm text-[var(--color-accent)] cursor-pointer">
              <input type="file" accept="image/*" className="hidden" onChange={onFile} />
              Scan another image
            </label>
          )}
        </div>

        <div>
          {attrs.length > 0 && (
            <div className="glass rounded-2xl p-4 mb-4 text-sm overflow-auto max-h-48">
              <h3 className="font-semibold mb-2">Smart attributes</h3>
              <pre className="text-zinc-400 whitespace-pre-wrap">{JSON.stringify(attrs, null, 2)}</pre>
            </div>
          )}
          <h3 className="font-semibold mb-4">Similar items</h3>
          <PinterestGrid items={items} />
        </div>
      </div>
    </motion.div>
  );
}
