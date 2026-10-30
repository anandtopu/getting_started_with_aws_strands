# Tier 2 | Knowledge and memory

Modules 07-09. [Printable PDF](../output/pdf/02_knowledge_memory.pdf).

## Mental model

Retrieval finds evidence; generation writes from that evidence. Memory retains selected user information. Neither source text nor memory can grant tool authority.

## RAG sequence

Load -> chunk -> embed/index -> retrieve -> rerank -> answer with citations. Compare retrieval scores and answer correctness separately.

## Local setup

uv sync --group rag --group memory
uv run python modules/07_rag/examples/01_load_and_chunk.py --mock

## Choose storage

BM25: lexical baseline. Vector search: semantic similarity. SQLite: explicit structured data. Managed Knowledge Bases and AgentCore Memory are optional AWS labs.

## Evaluate evidence

Use held-out questions with expected sources. Measure missing evidence and incorrect citations. An answer that sounds fluent can still fail the case.

## Memory boundaries

Ask for consent before saving preferences. Scope records by authenticated user. Treat recall as data. Test deletion and cross-user denial.

## Sessions vs memory

A session restores conversation state. Long-term memory stores selected facts across sessions. Keep retention and deletion policies explicit.

## Checkpoint and cleanup

Show a cited policy answer and consented preference recall. For optional AWS labs, destroy the resource stack and run scripts/find_leftovers.py --regions us-east-1.

See [the feature map](../docs/FEATURE_MAP.md) for source examples and [costs](../docs/COSTS.md) for live pricing.
