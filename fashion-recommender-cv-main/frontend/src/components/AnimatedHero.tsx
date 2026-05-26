import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";

export default function AnimatedHero() {
  return (
    <section className="relative rounded-3xl overflow-hidden glass p-8 md:p-14 mb-10">
      <motion.div
        className="absolute -top-20 -right-20 w-72 h-72 rounded-full blur-3xl opacity-40"
        style={{ background: "var(--color-primary)" }}
        animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
        transition={{ duration: 8, repeat: Infinity }}
      />
      <motion.div
        className="absolute -bottom-16 -left-16 w-56 h-56 rounded-full blur-3xl opacity-30"
        style={{ background: "var(--color-accent)" }}
        animate={{ y: [0, -20, 0] }}
        transition={{ duration: 6, repeat: Infinity }}
      />

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="relative z-10">
        <div className="flex items-center gap-2 text-sm text-[var(--color-accent)] mb-4">
          <Sparkles size={16} className="animate-pulse" />
          Full-stack AI fashion platform
        </div>
        <h1 className="text-4xl md:text-6xl font-bold leading-tight mb-4">
          Style smarter with{" "}
          <span className="shimmer-text">AI vision</span>
        </h1>
        <p className="text-zinc-400 max-w-xl text-lg mb-8">
          Pinterest-style discovery, 3D showcases, virtual try-on, and 10 powerful AI tools —
          built on FashionCLIP & YOLO.
        </p>
        <div className="flex flex-wrap gap-4">
          <Link
            to="/scan"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full font-semibold text-white shadow-lg transition-transform hover:scale-105"
            style={{ background: "linear-gradient(135deg, var(--color-primary), var(--color-accent))" }}
          >
            AI Scan <ArrowRight size={18} />
          </Link>
          <Link
            to="/studio"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full glass hover:bg-white/10"
          >
            Open AI Studio
          </Link>
        </div>
      </motion.div>
    </section>
  );
}
