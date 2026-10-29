"""Small inspectable retrieval components; synthetic embeddings are never model evidence."""

import hashlib
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from common.config import CourseError
from common.data import data_path


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    page: int
    topic: str

    def record(self) -> dict:
        return asdict(self)


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def split_text(text: str, size: int = 100, overlap: int = 20) -> list[str]:
    """Word windows, not tokenizer windows; validate progress before entering a loop."""
    if not 0 <= overlap < size:
        raise ValueError("Require 0 <= overlap < chunk size")
    words = text.split()
    return [" ".join(words[start : start + size]) for start in range(0, len(words), size - overlap)]


def load_chunks(*, pdf: bool = False, size: int = 100, overlap: int = 20) -> list[Chunk]:
    from pypdf import PdfReader

    pages = []
    if pdf:
        reader = PdfReader(data_path("policies/nimbus_terms.pdf"))
        pages = [
            ("policies/nimbus_terms.pdf", i + 1, page.extract_text() or "", "terms")
            for i, page in enumerate(reader.pages)
        ]
    else:
        pages = [
            (f"policies/{p.name}", 0, p.read_text(encoding="utf-8"), p.stem)
            for p in sorted(data_path("policies/refund.md").parent.glob("*.md"))
        ]
    chunks = []
    for source, page, text, topic in pages:
        for part, content in enumerate(split_text(text, size, overlap)):
            digest = hashlib.sha256(f"{source}:{page}:{part}:{content}".encode()).hexdigest()[:20]
            chunks.append(Chunk(digest, content, source, page, topic))
    return chunks


def cosine(left: list[float], right: list[float]) -> float:
    if not left or len(left) != len(right):
        raise ValueError("Vectors must have the same nonzero dimension")
    length = math.sqrt(sum(x * x for x in left) * sum(x * x for x in right))
    return sum(a * b for a, b in zip(left, right, strict=True)) / length if length else 0.0


def fixture_embeddings(texts: list[str], dimensions: int = 128) -> list[list[float]]:
    """Stable hashed word counts: a lexical fixture, not semantic embeddings."""
    result = []
    for text in texts:
        vector = [0.0] * dimensions
        for token in tokens(text):
            index = int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], "big") % dimensions
            vector[index] += 1.0
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        result.append([x / norm for x in vector])
    return result


class Embeddings:
    def __init__(self, *, mock: bool, host: str, model_id: str):
        self.mock, self.host, self.model_id = mock, host, model_id
        self.identity = "fixture-hash-128-v1" if mock else f"ollama:{host}:{model_id}"

    def __call__(self, texts: list[str]) -> list[list[float]]:
        if self.mock:
            return fixture_embeddings(texts)
        from ollama import Client

        response = Client(host=self.host, timeout=120).embed(
            model=self.model_id, input=texts, truncate=False
        )
        return response.embeddings


class LocalIndex:
    """Chroma receives explicit vectors, so it never downloads a default embedder."""

    def __init__(self, directory: Path, embed: Embeddings):
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError as exc:
            raise CourseError("Install retrieval tools: uv sync --group rag") from exc
        self.embed = embed
        self.client = chromadb.PersistentClient(
            path=str(directory), settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            "nimbus-policies",
            embedding_function=None,
            metadata={"embedding_identity": embed.identity},
            configuration={"hnsw": {"space": "cosine"}},
        )
        if self.collection.metadata.get("embedding_identity") != embed.identity:
            raise ValueError("Embedding model changed; build a separate index directory")

    def replace(self, chunks: list[Chunk]) -> None:
        if not chunks:
            raise ValueError("Cannot index an empty corpus")
        existing = self.collection.get()["ids"]
        if existing:
            self.collection.delete(ids=existing)
        self.collection.add(
            ids=[c.id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[{"source": c.source, "page": c.page, "topic": c.topic} for c in chunks],
            embeddings=self.embed([c.text for c in chunks]),
        )

    def search(self, query: str, k: int = 3, topic: str | None = None) -> list[dict]:
        if not 1 <= k <= 10:
            raise ValueError("Search limit must be between 1 and 10")
        if not self.collection.count():
            return []
        result = self.collection.query(
            query_embeddings=self.embed([query]),
            n_results=min(k, self.collection.count()),
            where={"topic": topic} if topic else None,
            include=["documents", "metadatas", "distances"],
        )
        return [
            {"id": ident, "text": text, **meta, "distance": distance}
            for ident, text, meta, distance in zip(
                result["ids"][0],
                result["documents"][0],
                result["metadatas"][0],
                result["distances"][0],
                strict=True,
            )
        ]


def lexical_search(
    chunks: list[Chunk], query: str, k: int = 3, topic: str | None = None
) -> list[Chunk]:
    """A simple executable baseline. BM25 and hybrid retrieval are separate upgrades."""
    words = set(tokens(query))
    candidates = [c for c in chunks if topic is None or c.topic == topic]
    scored = [(len(words & set(tokens(c.text))), c) for c in candidates]
    return [c for score, c in sorted(scored, key=lambda pair: (-pair[0], pair[1].id))[:k] if score]


def hybrid_search(chunks: list[Chunk], query: str, embed: Embeddings, k: int = 3) -> list[Chunk]:
    from rank_bm25 import BM25Okapi

    sparse = BM25Okapi([tokens(c.text) for c in chunks]).get_scores(tokens(query))
    query_vector = embed([query])[0]
    dense = [cosine(query_vector, vector) for vector in embed([c.text for c in chunks])]
    orders = [
        sorted(range(len(chunks)), key=lambda i: (-scores[i], chunks[i].id))
        for scores in (sparse, dense)
    ]
    # Reciprocal rank fusion combines ranks rather than incomparable score scales.
    fused = {i: sum(1 / (60 + order.index(i) + 1) for order in orders) for i in range(len(chunks))}
    return [chunks[i] for i in sorted(fused, key=lambda i: (-fused[i], chunks[i].id))[:k]]


def rerank(query: str, candidates: list[Chunk], k: int = 3) -> list[Chunk]:
    """Transparent local relevance heuristic; not a trained cross-encoder."""
    words = set(tokens(query)) - {"what", "the", "a", "is", "for", "how", "does", "and", "are"}

    def score(chunk: Chunk) -> float:
        return len(words & set(tokens(chunk.text))) / max(len(words), 1)

    return sorted(candidates, key=lambda c: (-score(c), c.id))[:k]
