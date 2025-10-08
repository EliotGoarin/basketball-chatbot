import React from "react"
import ChatBox from "./components/ChatBox.jsx"

export default function App(){
  return (
    <div>
      <h1 style={{marginBottom: 8}}>ChatBall🏀</h1>

      <div className="card">
        <ChatBox />
      </div>
      <p style={{marginTop: 16, opacity:.7}}>Backend: FastAPI — Front: React/Vite</p>
    </div>
  )
}
