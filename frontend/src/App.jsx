import React from "react"
import ChatBox from "./components/ChatBox.jsx"

export default function App(){
  return (
    <div>
      <h1 style={{marginBottom: 8}}>🏀 Basketball Chatbot (MVP)</h1>
      <p style={{opacity: .8, marginBottom: 16}}>
        Essaie <code>explique le goaltending</code> ou <code>stats Wembanyama 2024</code>.
      </p>
      <div className="card">
        <ChatBox />
      </div>
      <p style={{marginTop: 16, opacity:.7}}>Backend: FastAPI — Front: React/Vite</p>
    </div>
  )
}
