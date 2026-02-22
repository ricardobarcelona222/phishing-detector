from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from dotenv import load_dotenv
load_dotenv()

from app.database import engine
from app.models import Base

from app.routers.analysis_router import router as analysis_router
from app.routers.auth_router import router as auth_router
from app.routers.admin_router import router as admin_router
from app.routers.google_auth_router import router as google_auth_router
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pydantic import BaseModel
from app.database import SessionLocal
from app.models import User
from passlib.context import CryptContext
from app.database import SessionLocal
from app.models import User
from passlib.context import CryptContext
from app.database import SessionLocal
from app.models import User, PasswordResetToken
from passlib.context import CryptContext
from fastapi import HTTPException
from datetime import datetime

import re
from urllib.parse import urlparse

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear app
app = FastAPI(title="Phishing Detector API")

# Routers
app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(admin_router)
app.include_router(google_auth_router)

# Templates
templates = Jinja2Templates(directory="app/templates")

# Static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

# HTML routes
@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/admin")
def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})


@app.get("/google-success", response_class=HTMLResponse)
def google_success(request: Request):
    return templates.TemplateResponse("google_success.html", {"request": request})


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/reset-password")
def reset_password_page(request: Request, token: str):
    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "token": token}
    )


@app.get("/forgot-password")
def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        "forgot_password.html",
        {"request": request}
    )

@app.get("/change-password")
def change_password_page(request: Request):
    return templates.TemplateResponse("change_password.html", {"request": request})

# ==========================
# 🔥 Cargar modelo ML
# ==========================

MODEL_NAME = "Ricardo787848/phishing-detector-transformer"

device = torch.device("cpu")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

model.to(device)
model.eval()


# ==========================
#  Esquema de entrada
# ==========================
class PredictRequest(BaseModel):
    text: str




def analyze_urls(text: str):
    urls = re.findall(r'https?://[^\s]+', text)

    if not urls:
        return 0.0, []

    risk_score = 0.0
    triggers = []

    suspicious_tlds = [".xyz", ".info", ".ru", ".tk", ".top"]

    for url in urls:
        domain = urlparse(url).netloc.lower()

        if any(domain.endswith(tld) for tld in suspicious_tlds):
            risk_score += 0.4
            triggers.append("Dominio con TLD sospechoso")

        if domain.count("-") >= 2:
            risk_score += 0.2
            triggers.append("Dominio con múltiples guiones")

        if "@" in domain:
            risk_score += 0.3
            triggers.append("URL con estructura engañosa (@ detectado)")

    return min(risk_score, 1.0), triggers



def analyze_urgency(text: str):
    urgency_keywords = [
        "urgente", "inmediatamente", "último aviso", "ahora",
        "suspendida", "bloqueada", "verifica hoy",
        "24 horas", "acción requerida", "confirmar ahora"
    ]

    text_lower = text.lower()
    score = 0.0
    triggers = []

    for word in urgency_keywords:
        if word in text_lower:
            score += 0.2
            triggers.append(f"Lenguaje urgente detectado: '{word}'")

    return min(score, 0.6), triggers

def analyze_social_engineering(text: str):
    sensitive_keywords = [
        "contraseña", "password", "tarjeta", "cvv",
        "número de cuenta", "datos bancarios",
        "iniciar sesión", "login", "verificar identidad",
        "actualizar datos", "confirmar identidad"
    ]

    text_lower = text.lower()
    score = 0.0
    triggers = []

    for word in sensitive_keywords:
        if word in text_lower:
            score += 0.25
            triggers.append(f"Solicitud de dato sensible detectada: '{word}'")

    return min(score, 0.75), triggers


# ==========================
#  Endpoint predict
# ==========================
@app.post("/predict")
def predict(data: PredictRequest):

    text = data.text.strip()

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=1)

    model_score = probs[0][1].item()

    url_score, url_triggers = analyze_urls(text)
    urgency_score, urgency_triggers = analyze_urgency(text)
    social_score, social_triggers = analyze_social_engineering(text)

    contains_url = "http://" in text.lower() or "https://" in text.lower()

    # 🔥 CORRECCIÓN FUERTE DE SESGO
    if contains_url and url_score == 0 and urgency_score == 0 and social_score == 0:
        # Si SOLO tiene link y nada sospechoso
        # reducimos mucho el impacto del modelo
        model_weight = 0.25
    else:
        model_weight = 0.55

    final_score = (
        model_weight * model_score +
        0.25 * url_score +
        0.10 * urgency_score +
        0.10 * social_score
    )

    # 🔥 Penalización extra si modelo exagera solo por URL
    if contains_url and url_score == 0:
        final_score *= 0.75

    final_score = min(max(final_score, 0.0), 1.0)

    is_phishing = final_score > 0.5

    risk_factors = url_triggers + urgency_triggers + social_triggers

    # ==========================
    # 🔎 DEBUG PRINTS (IMPORTANTE)
    # ==========================
    print("----- DEBUG -----")
    print("Text:", text)
    print("Model score:", model_score)
    print("URL score:", url_score)
    print("Urgency score:", urgency_score)
    print("Social score:", social_score)
    print("Final score:", final_score)
    print("-----------------")

    return {
        "phishing_probability": round(final_score, 4),
        "is_phishing": is_phishing,
        "risk_factors": risk_factors
    }

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@app.post("/reset-password")
def reset_password(data: ResetPasswordRequest):

    db = SessionLocal()

    # 🔎 Buscar token en tabla PasswordResetToken
    reset_entry = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == data.token
    ).first()

    if not reset_entry:
        db.close()
        raise HTTPException(status_code=400, detail="Token inválido")

    # ⏰ Verificar expiración
    if reset_entry.expires_at < datetime.utcnow():
        db.delete(reset_entry)
        db.commit()
        db.close()
        raise HTTPException(status_code=400, detail="Token expirado")

    # 👤 Buscar usuario por email
    user = db.query(User).filter(User.email == reset_entry.email).first()

    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 🔐 Actualizar contraseña (IMPORTANTE: hashed_password)
    user.hashed_password = hash_password(data.new_password)

    # ❌ Borrar token después de usarlo
    db.delete(reset_entry)

    db.commit()
    db.close()

    return {"message": "Contraseña actualizada correctamente"}
