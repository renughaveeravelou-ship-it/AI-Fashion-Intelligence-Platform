import { motion } from "framer-motion";
import { Heart, ThumbsDown } from "lucide-react";
import { FashionItem, api } from "../lib/api";

type Props = {
  items: FashionItem[];
  onSelect?: (item: FashionItem) => void;
  showFeedback?: boolean;
};

export default function PinterestGrid({ items, onSelect, showFeedback = true }: Props) {
  if (!items.length) {
    return (
      <p className="text-center text-zinc-500 py-12">No items yet — try a search or scan.</p>
    );
  }

  return (
    <div className="pinterest-masonry">
      {items.map((item, i) => (
        <motion.div
          key={item.path + i}
          className="pinterest-item glass rounded-2xl overflow-hidden cursor-pointer group"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.04, duration: 0.4 }}
          whileHover={{ scale: 1.02, y: -4 }}
          onClick={() => onSelect?.(item)}
        >
          <div className="relative">
            <img
              src={item.url}
              alt={item.category}
              className="w-full h-auto object-cover"
              loading="lazy"
              style={{ minHeight: i % 3 === 0 ? 220 : i % 3 === 1 ? 160 : 280 }}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            {showFeedback && (
              <div className="absolute bottom-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    api.like(item.path);
                  }}
                  className="p-2 rounded-full bg-black/50 hover:bg-[var(--color-primary)]"
                >
                  <Heart size={14} />
                </button>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    api.dislike(item.path);
                  }}
                  className="p-2 rounded-full bg-black/50 hover:bg-red-500/80"
                >
                  <ThumbsDown size={14} />
                </button>
              </div>
            )}
          </div>
          <p className="px-3 py-2 text-xs text-zinc-400 truncate">{item.category}</p>
        </motion.div>
      ))}
    </div>
  );
}
