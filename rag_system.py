"""
Core rag_system class responsible for:
- Loading documents from the docs/ folder
- Building a simple retrieval index (Phase 1)
- Retrieving relevant snippets (Phase 1)
- Supporting retrieval only answers
- Supporting RAG answers when paired with Gemini (Phase 2)
"""

import os
import glob

_UNKNOWN = "I don't know."

_STOPWORDS = {
    "i", "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "where", "what", "when", "how",
    "why", "who", "which", "that", "this", "these", "those", "it", "its",
    "to", "of", "in", "on", "at", "by", "for", "with", "and", "or", "but",
    "not", "no", "so", "if", "as", "up", "my", "your", "we", "you", "they",
    "from", "about", "me", "us", "him", "her", "them", "their",
    # domain-specific high-frequency words that appear in nearly every paragraph
    "cat", "cats", "pet", "pets", "most", "also", "more",
    "very", "well", "often", "generally", "typically", "common", "commonly",
}

class rag_system:
    def __init__(self, docs_folder="docs", llm_client=None):
        """
        docs_folder: directory containing project documentation files
        llm_client: optional Gemini client for LLM based answers
        """
        self.docs_folder = docs_folder
        self.llm_client = llm_client

        # Load documents into memory
        self.documents = self.load_documents()  # List of (filename, text)

        # Build a retrieval index (implemented in Phase 1)
        self.index = self.build_index(self.documents)

    # -----------------------------------------------------------
    # Document Loading
    # -----------------------------------------------------------

    def load_documents(self):
        """
        Loads all .md and .txt files inside docs_folder.
        Returns a list of tuples: (filename, text)
        """
        docs = []
        pattern = os.path.join(self.docs_folder, "*.*")
        for path in glob.glob(pattern):
            if path.endswith(".md") or path.endswith(".txt"):
                with open(path, "r", encoding="utf8") as f:
                    text = f.read()
                filename = os.path.basename(path)
                docs.append((filename, text))
        return docs

    # -----------------------------------------------------------
    # Index Construction (Phase 1)
    # -----------------------------------------------------------

    def build_index(self, documents):
        """
        Build a tiny inverted index mapping lowercase words to the documents
        they appear in.

        Example structure:
        {
            "token": ["AUTH.md", "API_REFERENCE.md"],
            "database": ["DATABASE.md"]
        }

        Keep this simple: split on whitespace, lowercase tokens,
        ignore punctuation if needed.
        """
        index = {}
        for filename, text in documents:
            words = text.lower().split()
            for word in words:
                # Remove punctuation if needed (simple approach)
                word = ''.join(c for c in word if c.isalnum())
                if word:
                    if word not in index:
                        index[word] = []
                    if filename not in index[word]:
                        index[word].append(filename)
        return index

    # -----------------------------------------------------------
    # Scoring and Retrieval (Phase 1)
    # -----------------------------------------------------------

    def score_document(self, query, text):
        """
        Return a simple relevance score for how well the text matches the query.

        Suggested baseline:
        - Convert query into lowercase words
        - Count how many appear in the text
        - Return the count as the score
        """
        query_words = {
            ''.join(c for c in w if c.isalnum())
            for w in query.lower().split()
        } - _STOPWORDS

        text_words = {
            ''.join(c for c in w if c.isalnum())
            for w in text.lower().split()
        } - _STOPWORDS

        return len(query_words & text_words)

    def retrieve(self, query, top_k=3):
        """
        Use the index and scoring function to select top_k relevant document snippets.

        Return a list of (filename, text) sorted by score descending.
        """
        query_words = set(query.lower().split())
        candidate_filenames = set()
        for word in query_words:
            word = ''.join(c for c in word if c.isalnum())
            if word in self.index:
                candidate_filenames.update(self.index[word])

        doc_dict = {filename: text for filename, text in self.documents}

        clean_query_words = {
            ''.join(c for c in w if c.isalnum())
            for w in query.lower().split()
        }
        meaningful_words = clean_query_words - _STOPWORDS
        if not meaningful_words:
            return []

        scored = []
        for filename in candidate_filenames:
            paragraphs = [p.strip() for p in doc_dict[filename].split('\n\n') if p.strip()]
            for paragraph in paragraphs:
                para_words = {
                    ''.join(c for c in w if c.isalnum())
                    for w in paragraph.lower().split()
                }
                if meaningful_words & para_words:
                    score = self.score_document(query, paragraph)
                    scored.append((score, filename, paragraph))

        scored.sort(reverse=True)
        return [(filename, text) for _, filename, text in scored[:top_k]]

    # -----------------------------------------------------------
    # Answering Modes
    # -----------------------------------------------------------

    def answer_retrieval_only(self, query, top_k=3):
        """
        Phase 1 retrieval only mode.
        Returns raw snippets and filenames with no LLM involved.
        """
        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return _UNKNOWN

        formatted = []
        for filename, text in snippets:
            formatted.append(f"[{filename}]\n{text}\n")

        return "\n---\n".join(formatted)

    def answer_rag(self, query, top_k=3):
        """
        Phase 2 RAG mode.
        Uses student retrieval to select snippets, then asks Gemini
        to generate an answer using only those snippets.
        """
        if self.llm_client is None:
            raise RuntimeError(
                "RAG mode requires an LLM client. Provide a GeminiClient instance."
            )

        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return _UNKNOWN

        response = self.llm_client.answer_from_snippets(query, snippets)

        _uncertainty_markers = (
            "i don't know",
            "i do not know",
            "i cannot answer",
            "i'm not sure",
            "i am not sure",
            "the documents do not contain",
            "the provided documents do not",
        )
        if any(m in response.lower() for m in _uncertainty_markers):
            return _UNKNOWN

        return response

    # -----------------------------------------------------------
    # Bonus Helper: concatenated docs for naive generation mode
    # -----------------------------------------------------------

    def full_corpus_text(self):
        """
        Returns all documents concatenated into a single string.
        This is used in Phase 0 for naive 'generation only' baselines.
        """
        return "\n\n".join(text for _, text in self.documents)
