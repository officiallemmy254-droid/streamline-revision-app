from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from . import database, auth
from .documents import router as documents_router
from .revision import router as revision_router

app = FastAPI(
    title="Teacher Revision Skill API",
    description="Backend API for the Teacher Revision Skill web application.",
    version="0.1.0",
)

# CORS — allow the Vite dev server during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://streamline-revision-app-2026.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Schemas ──────────────────────
class RegisterRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str


# ── Database Dependency ─────────────────────────────
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Auth Endpoints ──────────────────────────────────
@app.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user account."""
    db_user = db.query(database.User).filter(
        database.User.username == payload.username
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    try:
        hashed_pwd = auth.hash_password(payload.password)
        new_user = database.User(username=payload.username, hashed_password=hashed_pwd)
        db.add(new_user)
        db.commit()
        return {"message": "User created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration error: {str(e)}"
        )

@app.get("/test_register")
def test_register(db: Session = Depends(get_db)):
    try:
        hashed_pwd = auth.hash_password("testpass123")
        new_user = database.User(username="testuser_get", hashed_password=hashed_pwd)
        db.add(new_user)
        db.commit()
        return {"message": "User created successfully via GET"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@app.post("/token", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate and receive a JWT access token."""
    user = db.query(database.User).filter(
        database.User.username == form_data.username
    ).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=MessageResponse)
def get_me(current_user: str = Depends(auth.get_current_user)):
    """Protected test endpoint — returns the authenticated username."""
    return {"message": f"Hello, {current_user}"}


# ── Health Check ────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok"}


# ── Mount Routers ───────────────────────────────────
app.include_router(documents_router)
app.include_router(revision_router)

from .notebooklm_router import router as notebooklm_router
app.include_router(notebooklm_router)

