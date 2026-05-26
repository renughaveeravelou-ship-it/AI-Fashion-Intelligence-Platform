import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import ProductCard3D from "../components/ProductCard3D";
import PinterestGrid from "../components/PinterestGrid";
import { api, FashionItem } from "../lib/api";

export default function Showcase3D() {
  const [items, setItems] = useState<FashionItem[]>([]);
  const [selected, setSelected] = useState<FashionItem | null>(null);

  useEffect(() => {
    api.feed(12).then((r) => {
      setItems(r.items);
      if (r.items[0]) setSelected(r.items[0]);
    });
  }, []);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <h1 className="text-3xl font-bold mb-2">3D Product Showcase</h1>
      <p className="text-zinc-400 mb-8">Rotate and explore catalog items in 3D</p>

      <div className="grid lg:grid-cols-2 gap-8 mb-10">
        <ProductCard3D item={selected} />
        <div className="max-h-[420px] overflow-y-auto">
          <PinterestGrid items={items} onSelect={setSelected} showFeedback={false} />
        </div>
      </div>
    </motion.div>
  );
}
