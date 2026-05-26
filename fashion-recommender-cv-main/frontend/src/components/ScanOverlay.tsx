import { motion } from "framer-motion";

export default function ScanOverlay({ active }: { active: boolean }) {
  if (!active) return null;
  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-2xl">
      <motion.div
        className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[var(--color-accent)] to-transparent shadow-[0_0_20px_var(--color-accent)]"
        animate={{ top: ["0%", "100%", "0%"] }}
        transition={{ duration: 2.5, repeat: Infinity, ease: "linear" }}
      />
      <div className="absolute inset-4 border-2 border-[var(--color-primary)]/50 rounded-xl" />
      <div className="absolute top-4 left-4 text-xs font-mono text-[var(--color-accent)] animate-pulse">
        SCANNING...
      </div>
    </div>
  );
}
