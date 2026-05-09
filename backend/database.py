from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    chunk_count = Column(Integer, default=0)
    category = Column(String, default="TEACHING_DIPLOMA")
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    document = relationship("Document", back_populates="chunks")


import sqlite3
import os

db_path = "./app.db"
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("ALTER TABLE documents ADD COLUMN category VARCHAR DEFAULT 'TEACHING_DIPLOMA'")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE users ADD COLUMN hashed_password VARCHAR")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE users ADD COLUMN created_at DATETIME")
        except Exception:
            pass
        conn.commit()
        conn.close()
    except Exception:
        pass

Base.metadata.create_all(bind=engine)
