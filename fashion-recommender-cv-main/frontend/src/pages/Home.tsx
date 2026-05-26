import { useEffect, useState } from "react";
import AnimatedHero from "../components/AnimatedHero";
import PinterestGrid from "../components/PinterestGrid";
import { api, FashionItem } from "../lib/api";
import { motion } from "framer-motion";

const features = [
  "Advanced AI", "Virtual Try-On", "Fashion Chatbot", "Trend Prediction",
  "Smart Attributes", "Personalized Engine", "Voice Search", "Image Captioning",
  "Multi-Modal Search", "Fashion Rating",
];

export default function Home() {
  const [items, setItems] = useState<FashionItem[]>([]);

  useEffect(() => {
    api.feed(24).then((r) => setItems(r.items)).catch(() => {});
  }, []);

  return (
    <>
      <AnimatedHero />
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex flex-wrap gap-2 mb-8"
      >
        {features.map((f) => (
          <span key={f} className="text-xs px-3 py-1 rounded-full glass text-zinc-300">
            {f}
          </span>
        ))}
      </motion.div>
      <h2 className="text-2xl font-bold mb-4">Trending looks</h2>
      <PinterestGrid items={items} />
    </>
  );
}
