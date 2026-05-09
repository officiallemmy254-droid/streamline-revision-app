"""
RAG Retriever — Simple keyword-based chunk retrieval.

Uses keyword matching instead of embeddings to avoid model availability issues.
Works entirely offline with zero API calls for retrieval.
"""


def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 300) -> list[str]:
    """Split text into overlapping chunks for retrieval."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def find_relevant_chunks(
    query: str,
    chunks: list[str],
    api_key: str = "",
    top_k: int = 3,
) -> list[str]:
    """
    Find the top-k most relevant chunks using keyword overlap scoring.

    This approach uses TF-based keyword matching instead of embeddings.
    It requires zero API calls, works offline, and is instant.
    """
    if not chunks:
        return []

    if len(chunks) <= top_k:
        return chunks

    # Tokenize query into keywords (lowercase, unique)
    query_words = set(query.lower().split())
    # Remove very short/common words
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "to", "of",
                  "and", "in", "that", "it", "for", "on", "with", "as", "at", "by",
                  "from", "or", "but", "not", "this", "they", "we", "i", "do", "if"}
    query_words = query_words - stop_words

    if not query_words:
        return chunks[:top_k]

    # Score each chunk by keyword overlap
    scores = []
    for i, chunk in enumerate(chunks):
        chunk_lower = chunk.lower()
        score = sum(1 for word in query_words if word in chunk_lower)
        # Bonus for longer keyword matches (phrases)
        for word in query_words:
            score += chunk_lower.count(word) * 0.1
        scores.append((score, i))

    # Sort by score descending, then by position (earlier chunks as tiebreaker)
    scores.sort(key=lambda x: (-x[0], x[1]))

    top_indices = [idx for _, idx in scores[:top_k]]
    return [chunks[i] for i in top_indices]
