"""
Phase 1 Verification Script
Run: python verify_phase1.py (from the project root)

Checks:
  1. All required files exist
  2. Backend imports work (dependencies installed)
  3. Database table creation works
  4. Password hashing round-trip works
  5. JWT token round-trip works
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
results = []


def check(name, fn):
    try:
        fn()
        print(f"  {PASS} {name}")
        results.append(True)
    except Exception as e:
        print(f"  {FAIL} {name}: {e}")
        results.append(False)


print("\n── Phase 1 Verification ──\n")

# 1. File existence
print("Files:")
required_files = [
    "backend/__init__.py",
    "backend/requirements.txt",
    "backend/database.py",
    "backend/auth.py",
    "backend/main.py",
    "frontend/package.json",
    "frontend/vite.config.ts",
    "frontend/src/App.tsx",
    "frontend/src/main.tsx",
    "frontend/src/index.css",
]
for f in required_files:
    check(f, lambda f=f: open(f).close())

# 2. Backend imports
print("\nImports:")
check("sqlalchemy", lambda: __import__("sqlalchemy"))
check("fastapi", lambda: __import__("fastapi"))
check("passlib", lambda: __import__("passlib"))
check("jose", lambda: __import__("jose"))

# 3. Database
print("\nDatabase:")


def test_db():
    from backend.database import engine, User, Base
    Base.metadata.create_all(bind=engine)
    assert User.__tablename__ == "users"


check("User model + create_all", test_db)

# 4. Auth
print("\nAuth:")


def test_password():
    from backend.auth import hash_password, verify_password
    h = hash_password("testpass123")
    assert verify_password("testpass123", h)
    assert not verify_password("wrongpass", h)


check("Password hash round-trip", test_password)


def test_jwt():
    from backend.auth import create_access_token, decode_access_token
    token = create_access_token({"sub": "testuser"})
    payload = decode_access_token(token)
    assert payload["sub"] == "testuser"


check("JWT token round-trip", test_jwt)

# 5. FastAPI app
print("\nAPI:")


def test_app():
    from backend.main import app
    routes = [r.path for r in app.routes]
    assert "/register" in routes
    assert "/token" in routes
    assert "/me" in routes
    assert "/health" in routes


check("All endpoints registered", test_app)

# Summary
print(f"\n── Results: {sum(results)}/{len(results)} passed ──\n")

# Cleanup test db if created
if os.path.exists("app.db"):
    os.remove("app.db")

sys.exit(0 if all(results) else 1)
