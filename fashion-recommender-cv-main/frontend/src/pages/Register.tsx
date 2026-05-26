import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "../lib/auth";

export default function Register() {
  const { register } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register(email, username, password);
      nav("/dashboard");
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Registration failed");
    }
  };

  return (
    <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="max-w-md mx-auto glass rounded-3xl p-8 mt-12">
      <h1 className="text-2xl font-bold mb-6 shimmer-text">Create account</h1>
      <form onSubmit={submit} className="space-y-4">
        <input type="email" required placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full p-3 rounded-xl bg-black/30 border border-white/10" />
        <input required placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} className="w-full p-3 rounded-xl bg-black/30 border border-white/10" />
        <input type="password" required placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full p-3 rounded-xl bg-black/30 border border-white/10" />
        {err && <p className="text-red-400 text-sm">{err}</p>}
        <button type="submit" className="w-full py-3 rounded-xl font-semibold text-white" style={{ background: "var(--color-primary)" }}>Register</button>
      </form>
      <p className="mt-4 text-sm text-zinc-500 text-center">
        Have an account? <Link to="/login" className="text-[var(--color-accent)]">Sign in</Link>
      </p>
    </motion.div>
  );
}
