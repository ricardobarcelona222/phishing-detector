from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests
import os

from app.auth import create_access_token
from app.database import SessionLocal
from app.models import User

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


# ----------------------
# LOGIN GOOGLE
# ----------------------
@router.get("/auth/google/login")
def google_login():

    google_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid email profile"
    )

    return RedirectResponse(google_url)


# ----------------------
# CALLBACK GOOGLE
# ----------------------
@router.get("/auth/google/callback")
def google_callback(code: str):

    token_url = "https://oauth2.googleapis.com/token"

    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    token_response = requests.post(token_url, data=data)
    token_json = token_response.json()

    if "id_token" not in token_json:
        raise HTTPException(status_code=400, detail="Google token error")

    idinfo = id_token.verify_oauth2_token(
        token_json["id_token"],
        google_requests.Request(),
        GOOGLE_CLIENT_ID
    )

    email = idinfo["email"]

    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.email == email,
            User.auth_provider == "google"
        ).first()

        # 🔹 Si no existe → crear como pendiente
        if not user:
            user = User(
                email=email,
                hashed_password="GOOGLE_LOGIN",
                role="user",
                auth_provider="google",
                is_approved=False  # 👈 IMPORTANTE
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 🚫 Si no está aprobado → no generar token
        if not user.is_approved:
         return RedirectResponse(
            url="/?error=pending"
        )

        # ✅ Solo si está aprobado generar token
        access_token = create_access_token({
            "sub": user.email,
            "role": user.role
        })

    finally:
        db.close()

    return RedirectResponse(
        url=f"/google-success?token={access_token}"
    )
