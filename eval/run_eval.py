import json
from pathlib import Path

from rag_app.config import get_settings
from rag_app.retrieval import HybridRetriever
from rag_app.vector_store import ChromaVectorStore


def main() -> None:
    settings = get_settings()
    retriever = HybridRetriever(ChromaVectorStore(settings))
    rows = [json.loads(line) for line in Path("eval/questions.jsonl").read_text().splitlines()]
    hits = 0
    for row in rows:
        retrieved = retriever.search(row["question"], top_k=settings.top_k)
        sources = {chunk.source for chunk in retrieved}
        expected = set(row["expected_sources"])
        passed = bool(sources & expected)
        hits += int(passed)
        print(f"{'PASS' if passed else 'FAIL'} | {row['question']} | got={sorted(sources)}")
    print(f"\nretrieval_hit_rate={hits / max(len(rows), 1):.2%}")


if __name__ == "__main__":
    main()
