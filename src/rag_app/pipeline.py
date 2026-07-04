from rag_app.config import get_settings
from rag_app.llm import generate_answer
from rag_app.retrieval import HybridRetriever
from rag_app.schemas import RetrievedChunk
from rag_app.vector_store import ChromaVectorStore


def answer_question(question: str, top_k: int | None = None) -> tuple[str, list[RetrievedChunk]]:
    settings = get_settings()
    store = ChromaVectorStore(settings)
    retriever = HybridRetriever(store)
    chunks = retriever.search(question, top_k or settings.top_k)
    if not chunks:
        return "I do not know. No relevant context was retrieved.", []
    answer = generate_answer(settings, question, chunks)
    return answer, chunks
