# Architecture decisions

- PostgreSQL is the source of truth for structured and changing business facts.
- Qdrant stores only document-derived chunks and metadata.
- Redis is reserved for cache, rate limiting, and short-lived agent state.
- Services coordinate use cases; repositories own persistence queries.
- LLM and embedding protocols keep provider SDKs outside business code.

