# Teacher Revision Skill Web App (Phase 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up the FastAPI backend, the React frontend, and implement secure user registration/login.

**Architecture**: 
- **Backend**: FastAPI with `pydantic` for validation and `sqlite` for persistence.
- **Frontend**: React (Vite) with `axios` for API calls and simple CSS.
- **Auth**: JWT tokens stored in `localStorage` (for prototype phase) or secure cookies.

---

### Task 1: Project Scaffolding

**Files:**
- Create: `backend/requirements.txt`
- Create: `frontend/` (via Vite)

- [ ] **Step 1: Create backend directory and requirements**
Create `backend/requirements.txt`:
```text
fastapi
uvicorn
sqlalchemy
passlib[bcrypt]
python-jose[cryptography]
python-multipart
```

- [ ] **Step 2: Create frontend directory (Vite)**
Run: `npm create vite@latest frontend -- --template react-ts`

- [ ] **Step 3: Initial Commit**
```bash
git add backend/ requirements.txt frontend/
git commit -m "chore: scaffold project structure"
```

---

### Task 2: Backend Database & User Models

**Files:**
- Create: `backend/database.py`

- [ ] **Step 1: Define User Schema in `backend/database.py`**
```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

Base.metadata.create_all(bind=engine)
```

- [ ] **Step 2: Commit**
```bash
git add backend/database.py
git commit -m "feat: add user database model"
```

---

### Task 3: Authentication Logic (JWT)

**Files:**
- Create: `backend/auth.py`

- [ ] **Step 1: Implement password hashing and token generation in `backend/auth.py`**
```python
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = "your-secret-key-change-this" # Placeholder
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

- [ ] **Step 2: Commit**
```bash
git add backend/auth.py
git commit -m "feat: implement JWT auth logic"
```

---

### Task 4: API Endpoints (Register & Login)

**Files:**
- Create: `backend/main.py`

- [ ] **Step 1: Create `backend/main.py` with Auth routes**
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import database, auth

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    db_user = db.query(database.User).filter(database.User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pwd = auth.hash_password(password)
    new_user = database.User(username=username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    return {"message": "User created"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(database.User).filter(database.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

- [ ] **Step 2: Commit**
```bash
git add backend/main.py
git commit -m "feat: add register and login endpoints"
```
