from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

# =========================
# CARGAR VARIABLES DE ENTORNO
# =========================
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "super_secreta_123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# =========================
# CREAR TOKEN
# =========================
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# =========================
# OBTENER USUARIO
# =========================
def get_current_user(token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email: str = payload.get("sub")
        role: str = payload.get("role")

        if email is None:
            raise credentials_exception

        return {
            "email": email,
            "role": role
        }

    except JWTError:
        raise credentials_exception


def get_current_admin(token: str = Depends(oauth2_scheme)):

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    role = payload.get("role")

    if role != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    return payload

def admin_required(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    email = current_user["email"]

    user = db.query(User).filter(User.email == email).first()

    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores")

    return user

