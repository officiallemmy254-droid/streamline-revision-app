# Context: Streamline — Tertiary Learner Revision App

## Domain Language
- **Streamline**: The core application designed to help any tertiary or high-level learner revise academic content through AI-powered active learning.
- **Revision Engine**: The AI-driven component that generates academic challenges and qualitative feedback.
- **Academic Challenge**: A realistic case study, problem scenario, counter-argument, or design brief requiring the learner to apply concepts from their uploaded material.
- **Learner Level**: The declared level of the user — Undergraduate, Postgraduate, or Professional (CPD) — used to calibrate Bloom's Taxonomy depth.
- **Active Learning**: The pedagogical principle driving the iterative challenge-response-feedback loop.
- **Bloom's Taxonomy**: The framework scaling from Comprehension+Application (UG) → Analysis+Synthesis (PG) → Evaluation+Creation (Professional).
- **Expert Academic Coach**: The AI persona — rigorous, cross-disciplinary, growth-oriented.
- **Minimal Risk AI**: Safety guidelines ensuring educational focus, no hallucination, and privacy.
- **Document Categories**: LECTURE_NOTES, TEXTBOOK_CHAPTER, PAST_EXAM, LEARNING_OUTCOMES, NOTES, TEACHING_DIPLOMA.

## Technical Context
- **AI Models**: Groq free-tier LLMs (llama-3.3-70b-versatile, llama3-70b-8192, gemma2-9b-it, mixtral-8x7b-32768).
- **Embeddings**: Google Gemini `text-embedding-004` (for RAG similarity).
- **RAG**: In-memory retrieval-augmented generation using cosine similarity.
- **Auth**: JWT (username/password, local SQLite).
- **Database**: SQLite via SQLAlchemy.
- **Frontend**: React + TypeScript + Vite.
