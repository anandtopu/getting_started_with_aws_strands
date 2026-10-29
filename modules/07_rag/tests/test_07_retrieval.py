"""Citation provenance and real vector persistence, independent of model quality."""

import pytest

from common.config import load_settings
from common.models import get_embeddings
from common.rag_agent import PolicyAnswer, answer_policy, validate_citations
from common.retrieval import Chunk, LocalIndex, cosine, load_chunks, split_text


def test_chunk_boundaries_and_pdf_provenance():
    with pytest.raises(ValueError):
        split_text("no progress", 2, 2)
    assert split_text("a b c d", 3, 1) == ["a b c", "c d"]
    chunks = load_chunks(pdf=True)
    assert any("5 to 10 business days" in c.text and c.page == 3 for c in chunks)
    assert {c.page for c in chunks} == set(range(1, 11))
    assert len({c.id for c in chunks}) == len(chunks)
    assert load_chunks() == load_chunks()


def test_cosine_and_dimension_mismatch():
    assert cosine([1, 0], [1, 0]) == 1
    assert cosine([0, 0], [1, 0]) == 0
    with pytest.raises(ValueError):
        cosine([1], [1, 2])


def test_real_agent_validates_citations_and_abstains_on_empty_corpus():
    cfg = load_settings(provider="mock")
    result, evidence = answer_policy(cfg, "refund timing", load_chunks(pdf=True))
    validate_citations(result.structured_output, evidence)
    result, _ = answer_policy(cfg, "What visa?", [])
    assert result.structured_output.abstained
    bad = PolicyAnswer(
        answer="invented",
        abstained=False,
        citations=[
            {
                "chunk_id": evidence[0].id,
                "source": evidence[0].source,
                "page": 999,
                "quote": evidence[0].text,
            }
        ],
    )
    with pytest.raises(ValueError, match="retrieved evidence"):
        validate_citations(bad, evidence)


def test_chroma_persistence_filters_and_embedding_identity(tmp_path):
    pytest.importorskip("chromadb")
    embed = get_embeddings(mock=True)
    index = LocalIndex(tmp_path, embed)
    index.replace(
        [
            Chunk("a", "refund timing", "refund.md", 0, "refund"),
            Chunk("b", "seat preference", "privacy.md", 0, "privacy"),
        ]
    )
    reopened = LocalIndex(tmp_path, embed)
    assert reopened.search("seat", topic="refund")[0]["id"] == "a"
    embed.identity = "different-model"
    with pytest.raises(ValueError, match="Embedding model changed"):
        LocalIndex(tmp_path, embed)
