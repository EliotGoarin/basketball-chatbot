import os
import re
from typing import List

class RulesRetriever:
    """
    Super-simple keyword retriever over small markdown files.
    - Loads *.md from rules_dir
    - Splits per blank line / heading into small chunks
    - Scores by keyword overlap count
    """

    def __init__(self, rules_dir: str, max_chunk_chars: int = 800):
        self.rules_dir = rules_dir
        self.max_chunk_chars = max_chunk_chars
        self._chunks: List[str] = []
        self._load_rules()

    def _load_rules(self):
        self._chunks.clear()
        if not os.path.isdir(self.rules_dir):
            return
        for name in sorted(os.listdir(self.rules_dir)):
            if not name.lower().endswith(".md"):
                continue
            path = os.path.join(self.rules_dir, name)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            for chunk in self._split_markdown(text):
                chunk = chunk.strip()
                if chunk:
                    # Clip chunks to reasonable size for prompt cost
                    self._chunks.append(chunk[: self.max_chunk_chars])

    def _split_markdown(self, text: str) -> List[str]:
        # Split on headings or blank lines groups
        blocks = re.split(r"(?:\n#+\s.*\n|\n{2,})", text)
        # Merge tiny blocks to avoid over-fragmentation
        merged: List[str] = []
        buf = ""
        for b in blocks:
            if not b or b.isspace():
                continue
            if len(buf) + len(b) < self.max_chunk_chars * 0.7:
                buf = (buf + "\n\n" + b).strip()
            else:
                if buf:
                    merged.append(buf)
                buf = b
        if buf:
            merged.append(buf)
        return merged

    def retrieve(self, query: str, k: int = 4) -> List[str]:
        if not self._chunks:
            return []
        q_words = self._tokenize(query)
        scored = []
        for ch in self._chunks:
            ch_words = self._tokenize(ch)
            overlap = len(q_words.intersection(ch_words))
            if overlap > 0:
                scored.append((overlap, ch))
        if not scored:
            # fallback: top-k first chunks
            return self._chunks[:k]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:k]]

    @staticmethod
    def _tokenize(s: str):
        s = s.lower()
        s = re.sub(r"[^a-z0-9\s]", " ", s)
        words = [w for w in s.split() if len(w) > 2]
        return set(words)
