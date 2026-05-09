# ADR 001: SaaS Stack Selection

## Status
Accepted

## Context
The project needs to transition from a Streamlit prototype to a scalable web application with authentication, persistence, and monitoring.

## Decision
We will use a modern SaaS stack to minimize infrastructure management and accelerate development:
- **Authentication**: Clerk (managed user sessions and multi-tenant isolation).
- **Database**: Supabase (PostgreSQL with built-in API support).
- **Analytics**: PostHog (event tracking for active learning usage).
- **Error Tracking**: Sentry (cross-stack observability).
- **DNS**: Cloudflare.

## Consequences
- Faster implementation of complex features (Auth, DB).
- Dependency on external service availability.
- Requirement for managing multiple API keys and environment variables.
