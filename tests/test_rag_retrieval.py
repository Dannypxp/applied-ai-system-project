import pytest
from rag_system import rag_system

DOCS_FOLDER = "docs"

@pytest.fixture
def bot():
    return rag_system(docs_folder=DOCS_FOLDER, llm_client=None)


def test_known_query_returns_result(bot):
    """A query with a clear match in the docs should return a non-unknown answer."""
    query = "Persian grooming coat"
    result = bot.answer_retrieval_only(query)
    print(f"\n  Query:  '{query}'")
    print(f"  Result: {result[:200]}...")
    assert result != "I don't know."
    assert len(result) > 0


def test_result_contains_source_filename(bot):
    """Returned snippets should include the source filename in brackets."""
    query = "Maine Coon size weight"
    result = bot.answer_retrieval_only(query)
    print(f"\n  Query:  '{query}'")
    print(f"  Result: {result[:200]}...")
    assert "[" in result and "]" in result


def test_unknown_query_returns_unknown(bot):
    """A query with no relevant terms in the docs should return the unknown sentinel."""
    query = "quantum entanglement spacecraft"
    result = bot.answer_retrieval_only(query)
    print(f"\n  Query:  '{query}'")
    print(f"  Result: '{result}'")
    assert result == "I don't know."


def test_all_stopwords_query_returns_unknown(bot):
    """A query made entirely of stopwords has no meaningful terms and should return unknown."""
    query = "what is the most"
    result = bot.answer_retrieval_only(query)
    print(f"\n  Query:  '{query}'")
    print(f"  Result: '{result}'")
    assert result == "I don't know."


def test_top_k_limits_snippets(bot):
    """Result should contain at most top_k snippets (default 3), separated by ---."""
    query = "health disease symptoms"
    top_k = 2
    result = bot.answer_retrieval_only(query, top_k=top_k)
    print(f"\n  Query:   '{query}'")
    print(f"  top_k:   {top_k}")
    if result != "I don't know.":
        snippet_count = result.count("\n---\n") + 1
        print(f"  Snippets returned: {snippet_count}")
        assert snippet_count <= top_k
    else:
        print(f"  Result:  '{result}'")
