import React, { useState, useRef, useEffect } from "react"
import { askChatStream } from "../api/client.js"

export default function ChatBox(){
  const [messages, setMessages] = useState([]) // {role:"user"|"assistant", content:string}[]
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [alert, setAlert] = useState(null) // {type, text}
  const streamHandle = useRef(null)
  const listRef = useRef(null)

  const suggestions = [
    "Explique la règle des 3 secondes",
    "Quelle est la différence entre marcher et double dribble ?",
    "Combien de temps dure un match officiel ?",
    "Que vaut un lancer franc ?",
  ]

  // Auto-scroll
  useEffect(() => {
    const el = listRef.current
    if (!el) return
    el.scrollTop = el.scrollHeight
  }, [messages])

  function appendAssistant(delta){
    setMessages(prev => {
      const last = prev[prev.length - 1]
      if (last && last.role === "assistant") {
        const updated = [...prev]
        updated[updated.length - 1] = { ...last, content: last.content + delta }
        return updated
      } else {
        return [...prev, { role: "assistant", content: delta }]
      }
    })
  }

  async function onSend(e){
    e?.preventDefault()
    const msg = input.trim()
    if (!msg || loading) return
    setAlert(null)
    setLoading(true)
    setMessages(prev => [...prev, { role: "user", content: msg }, { role: "assistant", content: "" }])
    setInput("")

    const history = [...messages, { role: "user", content: msg }]
    streamHandle.current = askChatStream(history, {
      top_k: 3,
      onDelta: (chunk) => appendAssistant(chunk),
      onDone: () => { setLoading(false); streamHandle.current = null },
      onError: (err) => {
        setLoading(false); streamHandle.current = null
        setAlert({ type: "error", text: err.message || "Erreur inconnue" })
      }
    })
  }

  function onStop(){
    if (streamHandle.current) {
      streamHandle.current.cancel()
      streamHandle.current = null
      setLoading(false)
    }
  }

  function onClickSuggestion(s) { setInput(s) }

  // ===== Styles responsables (centrage + tailles raisonnables) =====
  // Tailles responsive via clamp : petites sur petit écran, confortables sur large écran
  const sizes = {
    base: "clamp(0.90rem, 0.6vw + 0.7rem, 1.15rem)",     // texte général ~15–18px
    msg:  "clamp(0.90rem, 0.6vw + 0.7rem, 1.15rem)",         // texte des messages
    btn:  "clamp(0.95rem, 0.5vw + 0.7rem, 1.1rem)",       // boutons
    input:"clamp(0.80rem, 0.6vw + 0.8rem, 1.2rem)",          // input
    label:"clamp(0.8rem, 0.4vw + 0.6rem, 0.95rem)",       // “You / Chatball”
  }

  const containerStyle = {
    background:"#0b1220",
    border:"1px solid #24304a",
    borderRadius:16,
    padding:16,
    height: "75vh",                 // 3/4 écran
    display: "flex",
    flexDirection: "column",
    width: "min(88vw, 800px)",     // bien centré, pas trop large
    margin: "24px auto",            // centrage horizontal + marge top
    fontSize: sizes.base,
    lineHeight: 1.45,
  }

  const listStyle = {
    flex: 1,
    overflowY: "auto",
    padding: 14,
    background:"#0f1420",
    border:"1px solid #1f2942",
    borderRadius:12,
    marginBottom:12,
  }

  const bubbleBase = {
    display: "inline-block",
    maxWidth: "68ch",
    whiteSpace: "pre-wrap",
    wordWrap: "break-word",
    padding: "10px 12px",
    borderRadius: 12,
    border: "1px solid",
    fontSize: sizes.msg,
  }

  const bubbleAssistant = {
    ...bubbleBase,
    background: "#0e1a2e",
    borderColor: "#23304a",
    color: "#e9eef5",
  }

  const bubbleUser = {
    ...bubbleBase,
    background: "#1e2a46",
    borderColor: "#2f3e64",
    color: "#f0f6ff",
  }

  const rowBase = { display: "flex", marginBottom: 10 }

  const buttonBase = {
    padding:"8px 12px",
    borderRadius: 10,
    border:"1px solid #2a3550",
    background:"#10192a",
    color:"#dfe7f4",
    cursor:"pointer",
    fontSize: sizes.btn,
  }

  const inputStyle = {
    flex: 1,
    borderRadius: 12,
    border: "1px solid #2a3550",
    outline: "none",
    padding: "12px 14px",
    background:"#0f1420",
    color:"#e9eef5",
    fontSize: sizes.input,
  }

  return (
    <div style={containerStyle}>
      {alert && (
        <div style={{
          background:"#402020", border:"1px solid #6b3640", color:"#f3e6e6",
          borderRadius:10, padding:"8px 10px", marginBottom:12
        }}>
          {alert.text}
        </div>
      )}

      {/* Suggestions */}
      <div style={{ display:"flex", flexWrap:"wrap", gap:10, marginBottom:10 }}>
        {suggestions.map((s, i) => (
          <button key={i} onClick={() => onClickSuggestion(s)} style={buttonBase}>
            {s}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div ref={listRef} style={listStyle}>
        {messages.length === 0 && (
          <div style={{opacity:.7}}>
            💬 Pose une question — p.ex. <i>“Explique la règle des 3 secondes”</i>
          </div>
        )}

        {messages.map((m, i) => {
          const isUser = m.role === "user"
          return (
            <div
              key={i}
              style={{ ...rowBase, justifyContent: isUser ? "flex-end" : "flex-start" }}
            >
              <div style={isUser ? bubbleUser : bubbleAssistant}>
                <div style={{
                  opacity: .6,
                  marginBottom: 4,
                  textAlign: isUser ? "right" : "left",
                  fontSize: sizes.label
                }}>
                  {isUser ? "You" : "Chatball"}
                </div>
                <div>{m.content}</div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Input + actions */}
      <form onSubmit={onSend} style={{ display:"flex", gap: 8 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder={loading ? "Réponse en cours..." : "Écris ta question"}
          disabled={loading}
          style={inputStyle}
        />
        {!loading ? (
          <button type="submit" style={{ ...buttonBase, background:"#1b2335" }}>
            Envoyer
          </button>
        ) : (
          <button type="button" onClick={onStop} style={{ ...buttonBase, border:"1px solid #5a2a2a", background:"#3a1b1b" }}>
            Stop
          </button>
        )}
      </form>
    </div>
  )
}
