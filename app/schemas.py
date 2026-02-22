from pydantic import BaseModel
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from pydantic import BaseModel, EmailStr

from pydantic import BaseModel
from pydantic import BaseModel

class ForgotPasswordRequest(BaseModel):
    email: EmailStr



# =========================
# AUTH
# =========================

class AuthRequest(BaseModel):
    email: str
    password: str
    role: Optional[str] = "user"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# =========================
# EMAIL ANALYSIS
# =========================

class EmailRequest(BaseModel):
    text: str
    sender: Optional[str] = ""


class MessageRequest(BaseModel):
    text: str


# =========================
# ML RESPONSE
# =========================

class UrlPrediction(BaseModel):
    url: str
    prediction: str


class AnalysisResponse(BaseModel):
    phishing: bool
    risk_score: int
    risk_level: str
    reasons: List[str]
    urls_analyzed: List[UrlPrediction]

class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class EmailSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class AnalyzeRequest(BaseModel):
    message: str