# 🏀 Basketball Chatbot — MVP ++

Un chatbot **fonctionnel** qui permet :  
- d’**expliquer des règles de basket** (via un petit système de **RAG** sur des fichiers Markdown sourcés),  
- de fournir des **stats réelles de joueurs** (via l’API [balldontlie.io](https://balldontlie.io)),  
- de structurer les réponses avec un **LLM** (modèle HuggingFace, support LoRA optionnel).  

Stack : **FastAPI** (backend) + **React/Vite** (frontend).

---

## 🚀 Lancer le projet

### 1) Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Exemple avec un modèle léger (rapide CPU)
$env:MODEL_ID="Qwen/Qwen2.5-0.5B-Instruct"
$env:USE_LORA="0"
uvicorn app:app --reload --port 8000
```

> ⚠️ Si balldontlie te fournit une clé, ajoute-la :  
> `setx BALLDONTLIE_API_KEY "ta_clef"`

### 2) Frontend
```bash
cd ../frontend
npm i
npm run dev
```

- Frontend: http://localhost:5173  
- Backend: http://localhost:8000  

> Le proxy Vite redirige `/api/*` → backend.

---

## ✨ Fonctionnalités actuelles

- **Intent detection** simple (`rules_explanation`, `player_stats`, `small_talk`, `fallback`).  
- **Règles de jeu** : base locale en Markdown → indexée avec un mini moteur de recherche sémantique (RAG).  
- **Stats joueurs** : via `balldontlie` (nom + saison → moyennes, derniers matchs).  
  - Gestion des erreurs (401 si API key requise, 429 si rate limit, etc.)  
  - Extraction automatique du nom et de l’année dans le prompt.  
- **LLM HuggingFace** : génération de réponses structurées.  
  - Prompt engineering adapté aux règles vs aux stats.  
  - Support **LoRA** (pour styliser la réponse) activable avec `USE_LORA=1`.  
- **Robustesse** : pas de 500, toutes les erreurs sont capturées et renvoient une réponse lisible au client.  

---

## 🛠️ Endpoints

- `GET /health` → `{ ok: true }`  
- `POST /chat` → `{ message }` → `{ reply, intent }`

---

## 📂 Structure

```
backend/
  app.py              # routes FastAPI, orchestration intents → RAG ou balldontlie
  intents.py          # détection intent + extraction joueur/saison
  adapters/
    balldontlie.py    # wrapper API robuste (clé optionnelle)
  rag/
    indexer.py        # build de l’index local (Markdown rules)
    service.py        # recherche + formatage contextuel
  llm/
    client.py         # wrapper HuggingFace (LoRA optionnel)
    prompts.py        # templates prompts (rules vs stats)
frontend/
  vite.config.js      # proxy /api → backend
  src/api/client.js   # appels fetch /api/chat
  src/…               # UI React
```

---

## 📈 Prochaines évolutions

- **Cache mémoire** pour balldontlie (éviter les 429, accélérer).  
- **CI/CD** : GitHub Actions (lint + tests), Dockerfiles, déploiement Render/Railway.  
- **Tests** : pytest pour `intents`, RAG, balldontlie adapter.  
- **UX** : historique côté backend, avatars, copier-coller, thèmes.  
- **I18N** : FR/EN, préférences FIBA/NBA.  

---

## 📜 Licence
MIT  
