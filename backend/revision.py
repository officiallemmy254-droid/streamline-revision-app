"""
Revision Engine — Academic Challenge generator + Feedback loop.

Uses skill.md as system prompt context and Groq API (free models).
Retrieves relevant document chunks via keyword-based RAG before generating content.
Supports undergraduate, postgraduate, and professional (CPD) learner levels.
"""

import os
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

from . import database, auth
from .retriever import find_relevant_chunks

router = APIRouter(prefix="/revision", tags=["Revision Engine"])

# Load skill.md once at startup
SKILL_MD_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skill.md")
try:
    with open(SKILL_MD_PATH, "r", encoding="utf-8") as f:
        SKILL_LOGIC = f.read()
except FileNotFoundError:
    SKILL_LOGIC = "No skill.md found. Operate as a general academic coach."

# Free models on Groq
FREE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama3-70b-8192",
    "gemma2-9b-it",
    "mixtral-8x7b-32768"
]

# Valid learner levels
LEARNER_LEVELS = {"undergraduate", "postgraduate", "professional"}

# ── Schemas ─────────────────────────────────────────
class GenerateRequest(BaseModel):
    document_id: int
    gemini_api_key: str  # Groq API key
    learner_level: str = "undergraduate"  # undergraduate | postgraduate | professional


class FeedbackRequest(BaseModel):
    document_id: int
    scenario: str
    user_answer: str
    gemini_api_key: str  # Groq API key
    learner_level: str = "undergraduate"  # undergraduate | postgraduate | professional


class GenerateResponse(BaseModel):
    scenario: str
    document_name: str


class FeedbackResponse(BaseModel):
    feedback: str


class MessageResponse(BaseModel):
    message: str


# ── Dependency ──────────────────────────────────────
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_user_document(
    document_id: int, username: str, db: Session
) -> tuple[database.Document, list[str]]:
    """Get a document and its text chunks, verifying ownership."""
    user = db.query(database.User).filter(database.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    doc = db.query(database.Document).filter(
        database.Document.id == document_id,
        database.Document.user_id == user.id,
    ).first()

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    chunks = (
        db.query(database.DocumentChunk)
        .filter(database.DocumentChunk.document_id == doc.id)
        .order_by(database.DocumentChunk.chunk_index)
        .all()
    )
    chunk_texts = [c.content for c in chunks]

    # Also pull in supplementary documents (learning outcomes, notes, etc.)
    supplementary_categories = [
        "LEARNING_OUTCOMES", "NOTES", "LECTURE_NOTES", "TEXTBOOK_CHAPTER", "PAST_EXAM"
    ]
    extra_docs = db.query(database.Document).filter(
        database.Document.user_id == user.id,
        database.Document.category.in_(supplementary_categories),
        database.Document.id != doc.id
    ).all()

    for extra_doc in extra_docs:
        extra_chunks = (
            db.query(database.DocumentChunk)
            .filter(database.DocumentChunk.document_id == extra_doc.id)
            .order_by(database.DocumentChunk.chunk_index)
            .all()
        )
        for c in extra_chunks:
            chunk_texts.append(f"[{extra_doc.category}] {c.content}")

    return doc, chunk_texts


def _call_llm_with_retry(api_key: str, prompt: str) -> str:
    """Call Groq, handling rate limits with backoff."""
    env_api_key = os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")
    final_api_key = env_api_key if env_api_key else api_key
    
    if not final_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API Key is missing. Please provide it in the Dashboard or set GROQ_API_KEY in the .env file."
        )

    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=final_api_key,
    )

    errors = []
    
    for model_id in FREE_MODELS:
        for attempt in range(2):
            try:
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                err_str = str(e)
                if "429" in err_str:
                    print(f"[{model_id}] Rate limit hit. Waiting {2 ** attempt * 3} seconds...")
                    time.sleep(2 ** attempt * 3)
                    if attempt == 1:
                        errors.append(f"{model_id}: Rate Limit (429)")
                    continue
                else:
                    errors.append(f"{model_id}: {err_str}")
                    break

    error_summary = " | ".join(errors)
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"All Groq models failed. Details: {error_summary}",
    )


def _learner_level_instruction(level: str) -> str:
    """Return a Bloom's-aligned instruction string for the given learner level."""
    level = level.lower() if level else "undergraduate"
    instructions = {
        "undergraduate": (
            "The learner is an UNDERGRADUATE student. "
            "Target Bloom's levels: Comprehension and Application. "
            "Use clear, concrete language. Expect them to recall and apply key concepts. "
            "Keep the challenge focused and specific — avoid overwhelming complexity."
        ),
        "postgraduate": (
            "The learner is a POSTGRADUATE student. "
            "Target Bloom's levels: Analysis and Synthesis. "
            "Be intellectually rigorous. Expect them to compare frameworks, identify theoretical limitations, "
            "and construct well-reasoned arguments. Introduce genuine ambiguity that requires critical judgment."
        ),
        "professional": (
            "The learner is a PROFESSIONAL in continuing development (CPD). "
            "Target Bloom's levels: Evaluation and Creation. "
            "Treat them as a peer practitioner. Expect them to critique established approaches, "
            "weigh evidence against real-world constraints, and propose novel or adapted solutions. "
            "Use discipline-appropriate professional language."
        ),
    }
    return instructions.get(level, instructions["undergraduate"])


# ── Endpoints ───────────────────────────────────────
@router.post("/generate", response_model=GenerateResponse)
def generate_scenario(
    payload: GenerateRequest,
    current_user: str = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Generate an academic challenge based on uploaded document content using RAG."""
    if payload.learner_level not in LEARNER_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid learner_level. Must be one of: {', '.join(LEARNER_LEVELS)}",
        )

    doc, chunk_texts = _get_user_document(payload.document_id, current_user, db)

    if not chunk_texts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has no text content.",
        )

    seed_query = "core concepts, key arguments, frameworks, assessment criteria, and central theories"
    relevant_context = find_relevant_chunks(
        query=seed_query,
        chunks=chunk_texts,
        api_key=payload.gemini_api_key,
        top_k=3,
    )

    context_str = "\n---\n".join(relevant_context)
    level_instruction = _learner_level_instruction(payload.learner_level)

    prompt = f"""SYSTEM LOGIC (skill.md):
{SKILL_LOGIC}

LEARNER LEVEL INSTRUCTION:
{level_instruction}

DOCUMENT CONTEXT:
{context_str}

TASK: Based on the Academic Challenge Generator logic in the skill.md, create a new Academic Challenge.
It must be grounded in the provided document context but must NOT explicitly name the underlying theories or frameworks.
The challenge should be 100–160 words, realistic, and require genuine intellectual judgment to resolve.
Choose the most appropriate challenge type for this material (Case Study, Problem Scenario, Counter-argument, or Design Brief)."""

    scenario_text = _call_llm_with_retry(payload.gemini_api_key, prompt)

    return GenerateResponse(scenario=scenario_text, document_name=doc.filename)


@router.post("/feedback", response_model=FeedbackResponse)
def get_feedback(
    payload: FeedbackRequest,
    current_user: str = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Evaluate a learner's response against document content using RAG."""
    if payload.learner_level not in LEARNER_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid learner_level. Must be one of: {', '.join(LEARNER_LEVELS)}",
        )

    doc, chunk_texts = _get_user_document(payload.document_id, current_user, db)

    if not chunk_texts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has no text content.",
        )

    relevant_context = find_relevant_chunks(
        query=payload.user_answer,
        chunks=chunk_texts,
        api_key=payload.gemini_api_key,
        top_k=3,
    )

    context_str = "\n---\n".join(relevant_context)
    level_instruction = _learner_level_instruction(payload.learner_level)

    prompt = f"""SYSTEM LOGIC (skill.md):
{SKILL_LOGIC}

LEARNER LEVEL INSTRUCTION:
{level_instruction}

DOCUMENT CONTEXT:
{context_str}

ACADEMIC CHALLENGE PRESENTED:
{payload.scenario}

LEARNER'S RESPONSE:
{payload.user_answer}

TASK: Provide qualitative feedback using the Feedback Loop logic in skill.md.
Calibrate your expectations and language to the learner's level (see LEARNER LEVEL INSTRUCTION).
Structure your response with:
1. **Alignment** — How well did they identify and apply relevant concepts from the material?
2. **Gap Analysis** — What key ideas, nuances, or frameworks from the document did they overlook?
3. **Depth of Reasoning** — Is the argument/approach appropriate for their learner level?
4. **Next Steps** — Provide 2–3 specific "Dig Deeper" questions or actions grounded in the uploaded material.

Do NOT give a numerical grade. Do NOT generate personal data."""

    feedback_text = _call_llm_with_retry(payload.gemini_api_key, prompt)

    return FeedbackResponse(feedback=feedback_text)
