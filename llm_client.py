"""
Gemini client wrapper used by Pawpal+.

Handles:
- Configuring the Gemini client from the GEMINI_API_KEY environment variable
- Naive "generation only" answers over the full docs corpus (Phase 0)
- RAG style answers that use only retrieved snippets (Phase 2)

Experiment with:
- Prompt wording
- Refusal conditions
- How strictly the model is instructed to use only the provided context
"""

import os
import google.generativeai as genai

# Central place to update the model name if needed.
# You can swap this for a different Gemini model in the future.
GEMINI_MODEL_NAME = "gemini-2.5-flash"


class GeminiClient:
    """
    Simple wrapper around the Gemini model.

    Usage:
        client = GeminiClient()
        answer = client.naive_answer_over_full_docs(query, all_text)
        # or
        answer = client.answer_from_snippets(query, snippets)
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Missing GEMINI_API_KEY environment variable. "
                "Set it in your shell or .env file to enable LLM features."
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)

    # -----------------------------------------------------------
    # Phase 0: naive generation over full docs
    # -----------------------------------------------------------

    def naive_answer_over_full_docs(self, query, all_text):
        # We ignore all_text and send a generic prompt instead
        prompt = f"""
    You are a documentation assistant.
    Answer this developer question: {query}
    """
        response = self.model.generate_content(prompt)
        return (response.text or "").strip()

    def answer_general(self, query):
        """Fallback: answer a pet care question using Gemini's general knowledge."""
        prompt = f"""
You are a helpful pet care assistant for PawPal Ultra, a pet care planning app.

Answer the following pet owner question using your general knowledge.
Keep the answer friendly, concise, and practical.

Question: {query}
"""
        response = self.model.generate_content(prompt)
        return (response.text or "").strip()

    # -----------------------------------------------------------
    # Phase 2: RAG style generation over retrieved snippets
    # -----------------------------------------------------------

    def answer_from_snippets(self, query, snippets):
        """
        Phase 2:
        Generate an answer using only the retrieved snippets.

        snippets: list of (filename, text) tuples selected by DocuBot.retrieve
        """

        if not snippets:
            return "I do not know based on the docs I have."

        context_blocks = []
        for filename, text in snippets:
            block = f"[{filename}]\n{text}\n"
            context_blocks.append(block)

        context = "\n\n".join(context_blocks)

        prompt = f"""
You are a helpful pet care assistant for PawPal Ultra, a pet care planning app.

You will receive:
- A pet owner's question about pet care, health, behavior, or breeds
- A set of relevant snippets from the PawPal Ultra internal documentation

Your job:
- Answer the question in a friendly, concise way using the provided snippets.
- If the snippets do not contain enough information to answer confidently,
  reply exactly: "I do not know based on the docs I have."

Documentation snippets:
{context}

Owner's question:
{query}

Rules:
- Base your answer only on the provided snippets. Do not invent facts.
- Keep the answer conversational and practical for a pet owner.
- If you do answer, briefly note which document the information came from.
- If unsure, reply exactly: "I do not know based on the docs I have."
"""

        response = self.model.generate_content(prompt)
        return (response.text or "").strip()
