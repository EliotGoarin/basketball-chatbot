const BASE = import.meta.env.VITE_API_URL ?? ""

// classique (non-stream)
export async function askChat(messages, top_k = 3) {
  const res = await fetch(`${BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages, top_k }),
  })
  if (!res.ok) {
    let detail = ''
    try { const data = await res.json(); detail = data?.detail ? String(data.detail) : '' }
    catch { detail = await res.text().catch(() => '') }
    const err = new Error(detail || `HTTP ${res.status}`); err.status = res.status; throw err
  }
  return res.json()
}

// streaming: renvoie { cancel } et appelle onDelta(text) pour chaque chunk
export function askChatStream(messages, { top_k = 3, onDelta, onDone, onError } = {}) {
  const controller = new AbortController()
  const run = async () => {
    let res
    try {
      res = await fetch(`${BASE}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages, top_k }),
        signal: controller.signal,
      })
    } catch (e) {
      onError?.(new Error("Connexion interrompue ou bloquée."))
      return
    }
    if (!res.ok || !res.body) {
      let detail = ''
      try { const data = await res.json(); detail = data?.detail ? String(data.detail) : '' }
      catch { detail = await res.text().catch(() => '') }
      onError?.(new Error(detail || `HTTP ${res.status}`))
      return
    }
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ""
    try {
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        let idx
        while ((idx = buffer.indexOf("\n")) >= 0) {
          const line = buffer.slice(0, idx).trim()
          buffer = buffer.slice(idx + 1)
          if (!line) continue
          try {
            const obj = JSON.parse(line)
            if (obj.delta) onDelta?.(obj.delta)
            if (obj.done) { onDone?.(); return }
            if (obj.error) { onError?.(new Error(obj.error)); return }
          } catch {
            // ignore malformed line
          }
        }
      }
    } catch (e) {
      onError?.(new Error("Lecture du flux interrompue."))
    }
  }
  run()
  return { cancel: () => controller.abort() }
}
