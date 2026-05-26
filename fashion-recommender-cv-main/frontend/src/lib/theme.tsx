import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api, ThemeDef } from "./api";

const DEFAULT: ThemeDef = { id: "aurora", name: "Aurora", primary: "#8b5cf6", accent: "#ec4899" };

type ThemeCtx = { theme: ThemeDef; themes: ThemeDef[]; setThemeId: (id: string) => void };

const ThemeContext = createContext<ThemeCtx | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [themes, setThemes] = useState<ThemeDef[]>([DEFAULT]);
  const [theme, setTheme] = useState<ThemeDef>(() => {
    const saved = localStorage.getItem("themeId");
    return DEFAULT;
  });

  useEffect(() => {
    api.themes().then((r) => setThemes(r.themes)).catch(() => {});
  }, []);

  useEffect(() => {
    const saved = localStorage.getItem("themeId");
    const t = themes.find((x) => x.id === saved) || themes[0] || DEFAULT;
    setTheme(t);
    document.documentElement.style.setProperty("--color-primary", t.primary);
    document.documentElement.style.setProperty("--color-accent", t.accent);
  }, [themes]);

  const setThemeId = (id: string) => {
    localStorage.setItem("themeId", id);
    const t = themes.find((x) => x.id === id) || DEFAULT;
    setTheme(t);
    document.documentElement.style.setProperty("--color-primary", t.primary);
    document.documentElement.style.setProperty("--color-accent", t.accent);
  };

  return (
    <ThemeContext.Provider value={{ theme, themes, setThemeId }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme outside provider");
  return ctx;
}
