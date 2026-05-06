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
1. As a teacher, I want to create a secure account so that my revision materials and history are kept private.
2. As a teacher, I want to upload multiple PDF documents so that I can centralize all my Teaching Diploma resources.
3. As a teacher, I want the system to analyze my PDFs so that it can generate scenarios relevant to my specific curriculum.
4. As a teacher, I want to receive classroom dilemmas based on "Active Learning" theories so that I can practice my application skills.
5. As a teacher, I want to submit my answers to scenarios so that I can test my pedagogical judgment.
6. As a teacher, I want to receive qualitative feedback that cites specific theories from my PDFs so that I know exactly where I am aligned and where I have gaps.
7. As a teacher, I want "Next Steps" in my feedback so that I have a clear path for further reflection or study.
8. As a teacher, I want a modern dashboard so that I can easily navigate between my uploaded documents and practice sessions.
9. As an administrator, I want the system to follow "Minimal Risk" AI guidelines so that no personal student data is generated or stored.

## Implementation Decisions

### Architecture
- **Frontend**: React with TypeScript and Vanilla CSS for a responsive, high-fidelity UI.
- **Backend**: FastAPI (Python) for high performance and seamless integration with the Gemini AI libraries.
- **Authentication**: JWT-based auth with secure password hashing (using `passlib` and `python-jose`).
- **Database**: SQLite for metadata persistence (users, document references) to maintain simplicity in the initial phase.

### Modules
- **AuthModule**: Handles `/register`, `/login`, and `get_current_user` logic.
- **DocumentModule**: Handles file uploads to a secure storage path and text extraction via `PyPDF2`.
- **RevisionEngine**:
    - **Retriever**: Uses Gemini `text-embedding-004` to create and search vector representations of PDF chunks.
    - **Generator**: Uses Gemini `1.5-flash` to produce scenarios and feedback based on `skill.md` prompts.
- **UI Components**: `Dashboard`, `UploadZone`, `PracticeArena`, `FeedbackPanel`.

### API Contracts
- `POST /auth/register`: Create a new user.
- `POST /auth/token`: Login and receive JWT.
- `POST /documents/upload`: Upload PDF and trigger indexing.
- `GET /documents`: List user's documents.
- `POST /revision/generate`: Get a new scenario for a specific document.
- `POST /revision/feedback`: Submit an answer and get qualitative critique.

## Testing Decisions
- **Unit Tests**: Focus on the `RevisionEngine`'s ability to extract and chunk text correctly.
- **Integration Tests**: Verify the Auth middleware correctly blocks unauthorized access to the Document and Revision endpoints.
- **E2E Tests**: Use Playwright to verify the flow from login -> upload -> practice -> feedback.
- **Behavioral Testing**: Ensure the AI never provides numerical grades and always cites theories as defined in `skill.md`.

## Out of Scope
- Support for non-PDF file formats (Word, Powerpoint).
- Real-time collaborative revision sessions.
- Direct export of revision history to PDF.

## Further Notes
- The application will utilize the Gemini Free Tier; rate limiting must be handled gracefully in the backend.
- File storage will be local for the initial version.
