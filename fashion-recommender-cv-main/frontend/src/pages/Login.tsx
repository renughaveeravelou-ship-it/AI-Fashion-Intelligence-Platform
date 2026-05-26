import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "../lib/auth";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      nav("/dashboard");
    } catch {
      setErr("Invalid credentials");
    }
  };

  return (
    <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="max-w-md mx-auto glass rounded-3xl p-8 mt-12">
      <h1 className="text-2xl font-bold mb-6 shimmer-text">Sign in</h1>
      <form onSubmit={submit} className="space-y-4">
        <input type="email" required placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full p-3 rounded-xl bg-black/30 border border-white/10" />
        <input type="password" required placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full p-3 rounded-xl bg-black/30 border border-white/10" />
        {err && <p className="text-red-400 text-sm">{err}</p>}
        <button type="submit" className="w-full py-3 rounded-xl font-semibold text-white" style={{ background: "var(--color-primary)" }}>Sign in</button>
      </form>
      <p className="mt-4 text-sm text-zinc-500 text-center">
        No account? <Link to="/register" className="text-[var(--color-accent)]">Register</Link>
      </p>
    </motion.div>
  );
}
