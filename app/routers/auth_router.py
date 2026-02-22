from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.models import User
from app.schemas import AuthRequest
from app.security import hash_password, verify_password
from app.auth import create_access_token

import secrets
from datetime import datetime, timedelta
from app.models import PasswordResetToken
from pydantic import BaseModel
from app.schemas import ForgotPasswordRequest
from app.services.email_service import send_reset_email
from app.schemas import ChangePasswordRequest
from fastapi import Depends
from app.auth import get_current_user
from app.email_config import send_registration_email


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

router = APIRouter(tags=["Auth"])

@router.post("/register")
async def register(user: AuthRequest, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(
        User.email == user.email,
        User.auth_provider == "local"
    ).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        role="user",
        auth_provider="local",
        is_approved=False  # 👈 queda pendiente de aprobación
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ✅ Enviar correo de registro
    await send_registration_email(new_user.email)

    return {
        "message": "Usuario creado correctamente. Esperando aprobación del administrador."
    }
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == form_data.username,
        User.auth_provider == "local"
    ).first()

    # ❌ Usuario no existe o contraseña incorrecta
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

    # 🚫 Usuario no aprobado por admin
    if not user.is_approved:
        raise HTTPException(
            status_code=403,
            detail="Tu cuenta está pendiente de aprobación por el administrador."
        )

    # ✅ Crear token
    token = create_access_token({
        "sub": user.email,
        "role": user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }



from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="app/templates")


@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(request: Request, token: str):
    return templates.TemplateResponse(
        "reset_password.html",
        {
            "request": request,
            "token": token
        }
    )



@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    token = secrets.token_urlsafe(32)

    reset = PasswordResetToken(
        email=user.email,
        token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )

    db.add(reset)
    db.commit()
    print("Enviando correo a:", user.email)
    print("Token:", token)

    # ⭐ ESTA LINEA ES LA CLAVE
    send_reset_email(user.email, token)

    return {"message": "Correo de recuperación enviado"}


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Validar password actual
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")

    # Guardar nueva password
    current_user.hashed_password = hash_password(data.new_password)

    db.commit()

    return {"message": "Contraseña actualizada correctamente"}
