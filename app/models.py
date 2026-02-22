from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.database import Base
from datetime import datetime


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    phishing = Column(Boolean)
    risk_score = Column(Integer)
    risk_level = Column(String)
    reasons = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=False, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
    auth_provider = Column(String, default="local")
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    result = Column(String, nullable=False)  # phishing o safe
    date = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))


class PasswordResetToken(Base):

    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True)
    email = Column(String, index=True)
    token = Column(String, unique=True)
    expires_at = Column(DateTime)