# 🏀 Basketball Chatbot

Un chatbot **spécialisé dans le basketball**, capable d’expliquer les **règles officielles** et de répondre à des questions grâce à un système de **RAG (Retrieval Augmented Generation)** + **LLM local (Mistral via Ollama)**.

---

## 🚀 Stack technique

- **Backend** : FastAPI (Python)
- **Frontend** : React (Vite)
- **LLM** : [Ollama](https://ollama.com) avec modèle **Mistral** (par défaut)
- **Retriever** : système simple basé sur des fichiers Markdown (`backend/data/rules/`)
- **Streaming** : réponses générées en continu comme ChatGPT

---

## 📂 Arborescence simplifiée

```
backend/
  ├── app.py                # Entrée FastAPI
  ├── core/config.py        # Configuration & choix du provider
  ├── services/             # Retriever & providers (Anthropic, Mistral API, Ollama)
  ├── data/rules/           # Fichiers .md (base de connaissances)
  │     ├── 00_suggestions.md
  │     ├── 01_temps_de_jeu.md
  │     ├── 02_regles_deplacement.md
  │     └── ...
frontend/
  ├── src/components/ChatBox.jsx   # UI principale (chat streaming)
  ├── src/api/client.js            # Requêtes API (stream)
```

---

## 🔧 Installation

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Lancer l’API
uvicorn app:app --reload --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173  
- Backend: http://localhost:8000

Le proxy Vite redirige `/api/*` → backend.

---

## 🤖 Choix du LLM

Le provider est configuré via la variable d’environnement **LLM_PROVIDER** dans `backend/.env` :

- `ollama_mistral` → utilise Ollama local avec modèle **mistral**
- `mistral_api` → Mistral hébergé (API payante)
- `anthropic` → Claude (API payante)

### Exemple `.env` minimal pour Ollama

```
LLM_PROVIDER=ollama_mistral
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=mistral

RETRIEVER_MAX_CHARS_PER_CHUNK=400
```

---

## ✨ Fonctionnalités actuelles

- Répond aux questions sur les **règles du basket**
- Base de règles en fichiers `.md` (retriever local)
- Réponses **streaming** (affichées au fur et à mesure)

---

## 📌 À faire ensuite

- Ajouter plus de règles et de contenus dans `backend/data/rules`
- Créer d'autres dossiers dans data contenant d'autres informations que les règles. 
- Connecter àa une API spécialisée en basket (BallDontLie) pour aller chercher les informations mises à jour/actuelles
- Améliorer la présentation UI (historique, avatars, thèmes)
- Héberger le projet en ligne (backend + frontend)
- Éventuellement activer des providers distants (Mistral API / Anthropic)
- Créer des modes pour le chatbot -> différents sports, différents types d'infos (medecin du sport, arbitre, reporter sportif ?).
---

## ⚠️ Note importante : gestion des secrets

- Le fichier `.env` **ne doit pas être versionné** (ajouté au `.gitignore`)
- Fournir un `.env.example` pour partager la structure sans clés sensibles

---
