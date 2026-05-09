---
status: resolved
trigger: Registration failed with 500 Internal Server Error
created: 2026-05-07T18:25:00
updated: 2026-05-07T18:42:00
---

# Debug Session: registration-500-error

## Symptoms
- **Expected behavior**: Submitting the registration form should create a new user in the database and redirect to the login page.
- **Actual behavior**: The application shows a generic "Registration failed. Please try again." message.
- **Error messages**: The backend returns a 500 Internal Server Error when hitting the `POST /api/register` endpoint.
- **Timeline**: Issue has existed since the endpoint was first implemented; it has never worked successfully.
- **Reproduction**: Go to http://localhost:5173/register, fill in a username and matching passwords, and click "Create Account".

## Current Focus
**hypothesis**: The `users` table in SQLite is missing the `hashed_password` and `created_at` columns because it was created in a previous iteration without authentication.
**next_action**: None (Resolved)

## Evidence
- The backend threw a 500 Internal Server Error exclusively on the `/register` endpoint.
- Code inspection of `backend/main.py` shows `db.add(new_user)` was called before the crash.
- `database.py` defines `hashed_password` on `User`, but `Base.metadata.create_all()` does not alter existing tables in SQLite.

## Eliminated
- Password hashing logic (`auth.py` uses standard library, no missing dependencies).

## Resolution
**root_cause**: Schema mismatch in `app.db`. The `users` table existed but lacked the newly added authentication columns (`hashed_password`, `created_at`).
**fix**: Added explicit `ALTER TABLE` schema migrations in `backend/database.py` on startup, and wrapped the `register` endpoint in a `try...except` block to surface exact error details.
**files_changed**: `backend/database.py`, `backend/main.py`
