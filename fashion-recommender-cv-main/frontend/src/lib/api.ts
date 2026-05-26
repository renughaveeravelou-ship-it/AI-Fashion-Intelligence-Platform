export type FashionItem = { path: string; url: string; category: string };

const API = "/api";

function authHeaders(): HeadersInit {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function parse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export type ThemeDef = { id: string; name: string; primary: string; accent: string };

export const api = {
  health: () => fetch(`${API}/health`).then((r) => r.json()),

  register: async (email: string, username: string, password: string) =>
    parse<{ token: string; user: { id: number; email: string; username: string } }>(
      await fetch(`${API}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, username, password }),
      })
    ),

  login: async (email: string, password: string) =>
    parse<{ token: string; user: { id: number; email: string; username: string } }>(
      await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })
    ),

  feed: async (limit = 48) =>
    parse<{ items: FashionItem[] }>(await fetch(`${API}/catalog/feed?limit=${limit}`)),

  dashboard: async () =>
    parse<Record<string, unknown>>(await fetch(`${API}/dashboard/stats`, { headers: authHeaders() })),

  themes: async () => parse<{ themes: ThemeDef[] }>(await fetch(`${API}/dashboard/themes`)),

  searchText: async (query: string, category = "All") => {
    const fd = new FormData();
    fd.append("query", query);
    fd.append("category", category);
    return parse<{ items: FashionItem[] }>(
      await fetch(`${API}/ai/search/text`, { method: "POST", headers: authHeaders(), body: fd })
    );
  },

  searchImage: async (file: File, category = "All") => {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("category", category);
    return parse<{ items: FashionItem[]; attributes?: unknown[] }>(
      await fetch(`${API}/ai/search/image`, { method: "POST", headers: authHeaders(), body: fd })
    );
  },

  multimodal: async (text: string, file: File | null, textWeight: number, category = "All") => {
    const fd = new FormData();
    fd.append("text", text);
    fd.append("text_weight", String(textWeight));
    fd.append("category", category);
    if (file) fd.append("file", file);
    return parse<{ items: FashionItem[] }>(
      await fetch(`${API}/ai/search/multimodal`, { method: "POST", headers: authHeaders(), body: fd })
    );
  },

  advanced: async (file: File, text: string, category = "All") => {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("text", text);
    fd.append("category", category);
    return parse<{ items: FashionItem[]; attributes: unknown[] }>(
      await fetch(`${API}/ai/advanced`, { method: "POST", headers: authHeaders(), body: fd })
    );
  },

  tryOn: async (person: File, garment: File, region: string) => {
    const fd = new FormData();
    fd.append("person", person);
    fd.append("garment", garment);
    fd.append("region", region);
    return parse<{ image_base64: string }>(
      await fetch(`${API}/ai/try-on`, { method: "POST", headers: authHeaders(), body: fd })
    );
  },

  chat: async (message: string) => {
    const fd = new FormData();
    fd.append("message", message);
    return parse<{ reply: string; items: FashionItem[] }>(
      await fetch(`${API}/ai/chat`, { method: "POST", headers: authHeaders(), body: fd })
    );
  },

  trends: async () => parse<Record<string, unknown>>(await fetch(`${API}/ai/trends`)),

  attributes: async (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return parse<{ attributes: Record<string, unknown>[] }>(
      await fetch(`${API}/ai/attributes`, { method: "POST", body: fd })
    );
  },

  caption: async (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return parse<{ caption: string }>(await fetch(`${API}/ai/caption`, { method: "POST", body: fd }));
  },

  rate: async (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return parse<{ rating: number; label: string; breakdown: Record<string, number> }>(
      await fetch(`${API}/ai/rate`, { method: "POST", body: fd })
    );
  },

  voice: async (file: File, category = "All") => {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("category", category);
    return parse<{ transcript: string | null; items: FashionItem[]; error?: string }>(
      await fetch(`${API}/ai/voice`, { method: "POST", headers: authHeaders(), body: fd })
    );
  },

  personalized: async (query: string, personalized = true, category = "All") => {
    const fd = new FormData();
    fd.append("query", query);
    fd.append("personalized", String(personalized));
    fd.append("category", category);
    return parse<{ items: FashionItem[]; profile_active: boolean }>(
      await fetch(`${API}/ai/personalized`, { method: "POST", headers: authHeaders(), body: fd })
    );
  },

  like: async (path: string) => {
    const fd = new FormData();
    fd.append("path", path);
    return fetch(`${API}/ai/feedback/like`, { method: "POST", headers: authHeaders(), body: fd });
  },

  dislike: async (path: string) => {
    const fd = new FormData();
    fd.append("path", path);
    return fetch(`${API}/ai/feedback/dislike`, { method: "POST", headers: authHeaders(), body: fd });
  },
};
