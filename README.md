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


1. Améliorations RAG (retriever) Passer d’un retriever basique → vectoriel Intégrer une base vectorielle (FAISS ou Chroma) pour chercher les passages de règles. Utiliser des embeddings multilingues (ex. sentence-transformers). Gestion multilingue Si question en français, chercher avec embeddings FR ; si anglais, chercher avec embeddings EN. Meilleure segmentation des règles Actuellement découpées en chunks par taille → segmenter plutôt par sections logiques (titres, articles). Score de confiance Si aucun passage n’atteint un seuil → le bot dit “Désolé, je n’ai pas trouvé la règle correspondante”.
2. Gestion des réponses du LLM Forcer la langue de sortie (toujours FR si utilisateur parle FR). Réponses formatées Titres, puces, exemples concrets. Citations directes des fichiers .md si pertinent. Mode “strict” Si pas de contexte fourni par le retriever → refuser de répondre (au lieu d’inventer).

3. Améliorations UI/UX Historique de chat (sauvegarde des conversations localement ou en DB). Avatars + bulles différenciées (ex. logo basket pour le bot). Indication de “pensée” (loading animé pendant la génération). Mode clair/sombre. Bouton “clear chat”.

4. Contenu et connaissances Enrichir backend/data/rules/ : Ajouter plus de règles officielles (FIBA, NBA, NCAA). Ajouter glossaire de termes (pick-and-roll, alley-oop, etc.). Stats et anecdotes : Ajouter un fichier fun_facts.md avec records NBA, grands joueurs, etc. Permettre au retriever de ressortir ça aussi. FAQ pour utilisateurs débutants (ex : “Comment dribbler correctement ?”).

5. Hébergement et performance Déploiement backend : Render, Railway, ou VPS perso. Déploiement frontend : Vercel, Netlify. Cache local pour ne pas réinterroger Ollama si la question est identique. Monitoring : logs des requêtes + temps de réponse.

6. Bonus avancés Mode entraînement joueur Donner des exercices de dribble, shoot, condition physique. Mode quiz Le bot pose des questions de règles à l’utilisateur. Personnalité configurable Ex : bot sérieux (arbitre) ou fun (commentateur NBA). Multi-LLM Utiliser Ollama Mistral pour les règles → fallback sur un modèle plus costaud (Claude, GPT-4) pour les stats récentes.
---
