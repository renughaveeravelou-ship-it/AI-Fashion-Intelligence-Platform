# Smart Stylist — Full Stack

Modern React UI + FastAPI backend. **All 10 original AI features are preserved** in AI Studio (and via API). Streamlit (`home.py`) still works independently.

## Run full stack

**One command (opens two terminals):**
```powershell
.\run_all.ps1
```

**Or manually:**

**Terminal 1 — API (from project root):**
```powershell
.\run_backend.ps1
```

**Terminal 2 — Frontend:**
```powershell
.\run_frontend.ps1
```

- **Web app:** http://localhost:5173  
- **API docs:** http://127.0.0.1:8000/docs  
- **Streamlit (legacy):** `streamlit run home.py` → http://localhost:8501  

## New platform features

| Feature | Page |
|---------|------|
| Full stack (React + FastAPI) | Entire app |
| Modern UI + animations | All pages (Framer Motion) |
| Pinterest grid | Discover, Home |
| AI Scan screen | `/scan` |
| 3D product showcase | `/showcase` |
| Dashboard | `/dashboard` |
| Authentication | `/login`, `/register` |
| AI theme styling | Sidebar theme picker |
| Mobile responsive | Tailwind breakpoints |

## Preserved AI features (AI Studio `/studio`)

1. Advanced AI · 2. Virtual Try-On · 3. Fashion Chatbot · 4. Trend Prediction  
5. Smart Attributes · 6. Personalized Engine · 7. Voice Search  
8. Image Captioning · 9. Multi-Modal Search · 10. Fashion Rating  
