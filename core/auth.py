import os
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)

def get_db_engine():
    # If DATABASE_URL is set in environment (e.g. Streamlit Cloud secrets), use it.
    # Otherwise, default to local SQLite database.
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        try:
            if "DATABASE_URL" in st.secrets:
                database_url = st.secrets["DATABASE_URL"]
        except Exception:
            pass
        
    if database_url:
        # Use postgresql (ensure URL starts with postgresql:// not postgres:// for SQLAlchemy)
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        engine = create_engine(database_url)
    else:
        # Default to SQLite
        engine = create_engine("sqlite:///app_database.db", connect_args={"check_same_thread": False})
    
    Base.metadata.create_all(engine)
    return engine

engine = get_db_engine()
SessionLocal = sessionmaker(bind=engine)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(username, password):
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return False, "Username already exists."
        
        hashed = hash_password(password)
        new_user = User(username=username, password_hash=hashed)
        db.add(new_user)
        db.commit()
        return True, "User registered successfully!"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()

def login_user(username, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password_hash):
            return True, "Login successful!"
        return False, "Invalid username or password."
    finally:
        db.close()
