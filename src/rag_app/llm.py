from groq import Groq

from rag_app.config import Settings
from rag_app.schemas import RetrievedChunk

SYSTEM_PROMPT = """You are an enterprise policy assistant.
Answer only from the supplied context. If the answer is not present, say you do not know.
Be concise, cite sources inline like [source, p. 2], and avoid inventing policy details."""


def build_context(chunks: list[RetrievedChunk]) -> str:
    lines = []
    for idx, chunk in enumerate(chunks, start=1):
        page = f", page {chunk.page}" if chunk.page else ""
        lines.append(f"[Context {idx}: {chunk.source}{page}; score={chunk.score:.3f}]\n{chunk.text}")
    return "\n\n".join(lines)


def generate_answer(settings: Settings, question: str, chunks: list[RetrievedChunk]) -> str:
    client = Groq(api_key=settings.groq_api_key)
    context = build_context(chunks)
    completion = client.chat.completions.create(
        model=settings.groq_model,
        temperature=0.1,
        max_tokens=800,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer with citations.",
            },
        ],
    )
    return completion.choices[0].message.content or ""
