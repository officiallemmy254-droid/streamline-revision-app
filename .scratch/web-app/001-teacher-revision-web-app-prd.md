---
title: Teacher Revision Skill Web Application
status: needs-triage
labels: ["needs-triage"]
---

# PRD: Teacher Revision Skill Web Application

## Problem Statement
Educators need a structured and interactive way to revise Teaching Diploma content that goes beyond passive reading. Current methods lack the ability to practice real-world application of theories in a safe, classroom-like environment with expert feedback. Colleagues also need a centralized, secure platform where they can manage their own revision materials and progress.

## Solution
A full-stack web application that allows teachers to securely upload their Teaching Diploma PDFs and engage with an AI-driven "Revision Engine". The app uses in-memory RAG to generate realistic classroom dilemmas (Bloom's Application level) and provide qualitative pedagogical feedback (Bloom's Evaluation level) based strictly on the uploaded materials.

## User Stories
1. As a learner, I want to create a secure account so that my revision materials and history are kept private.
2. As a learner, I want to upload multiple PDF documents so that I can centralise all my study resources.
3. As a learner, I want the system to analyse my PDFs so that it can generate challenges relevant to my specific curriculum.
4. As a learner, I want to receive academic challenges calibrated to my learner level so that I can practise applying the right depth of reasoning.
5. As a learner, I want to submit my responses to challenges so that I can test my understanding.
6. As a learner, I want to receive qualitative feedback that cites specific concepts from my uploaded material so that I know exactly where I am aligned and where I have gaps.
7. As a learner, I want "Dig Deeper" next steps in my feedback so that I have a clear path for further reflection or study.
8. As a learner, I want a modern dashboard so that I can easily navigate between my uploaded documents and practice sessions.
9. As a learner, I want to **export my revision history to PDF** so that I can review my progress offline or submit it as evidence of self-study.
10. As an administrator, I want the system to follow "Minimal Risk" AI guidelines so that no personal data is generated or stored.

## Implementation Decisions

### Architecture
- **Frontend**: React with TypeScript and Vanilla CSS.
- **Backend**: FastAPI (Python) for AI orchestration and RAG logic.
- **Authentication**: Clerk (managed authentication) with middleware in FastAPI to verify tokens.
- **Database**: Supabase (managed PostgreSQL) for storing user profiles and document metadata.
- **Infrastructure & Monitoring**: 
  - **DNS**: Cloudflare.
  - **Analytics**: PostHog.
  - **Error Tracking**: Sentry.

### Modules
- **AuthModule**: Integrates Clerk SDK on the frontend and validates Clerk JWTs on the FastAPI backend.
- **DocumentModule**: Handles file uploads (potentially leveraging Supabase Storage) and text extraction via `PyPDF2`.
- **RevisionEngine**:
    - **Retriever**: Uses Gemini `text-embedding-004` to create and search vector representations of PDF chunks.
    - **Generator**: Uses Gemini `1.5-flash` to produce scenarios and feedback based on `skill.md` prompts.
- **Observability**: PostHog integrated for user event tracking; Sentry integrated on both frontend and backend for crash reporting.

### API Contracts
- `POST /documents/upload`: Upload PDF (authenticated).
- `GET /documents`: List user's documents (authenticated).
- `DELETE /documents/{id}`: Delete a document and its chunks (authenticated).
- `POST /revision/generate`: Get a new academic challenge for a specific document (authenticated).
- `POST /revision/feedback`: Submit a response and get qualitative critique (authenticated).
- `GET /revision/history`: Retrieve the user's revision session history (authenticated).
- `GET /revision/history/export`: Export the full revision history as a downloadable PDF (authenticated).

## Testing Decisions
- **Unit Tests**: Focus on the `RevisionEngine`'s ability to extract and chunk text correctly.
- **Integration Tests**: Verify the Auth middleware correctly blocks unauthorized access to the Document and Revision endpoints.
- **E2E Tests**: Use Playwright to verify the flow from login -> upload -> practice -> feedback.
- **Behavioral Testing**: Ensure the AI never provides numerical grades and always cites theories as defined in `skill.md`.

## Out of Scope
- Support for non-PDF file formats (Word, PowerPoint).
- Real-time collaborative revision sessions.

## Further Notes
- The application will utilize the Gemini Free Tier; rate limiting must be handled gracefully in the backend.
- File storage will be local for the initial version.
