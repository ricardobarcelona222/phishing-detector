from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.models import AnalysisResult
from app.email_config import send_approval_email

router = APIRouter(prefix="/admin", tags=["Admin"])


# =========================
# VALIDAR ADMIN
# =========================
def admin_required(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    email = current_user["email"]

    user = db.query(User).filter(User.email == email).first()

    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores")

    return user


# =========================
# LISTAR USUARIOS
# =========================
@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    user = Depends(admin_required)
):

    users = db.query(User).all()

    return [
    {
        "id": u.id,
        "email": u.email,
        "role": u.role,
        "is_admin": u.role == "admin",
        "is_approved": u.is_approved
    }
    for u in users
]


# =========================
# ELIMINAR USUARIO
# =========================
@router.delete("/delete-user/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user = Depends(admin_required)
):

    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(db_user)
    db.commit()

    return {"message": "Usuario eliminado"}


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    user = Depends(admin_required)
):
    total = db.query(AnalysisResult).count()

    phishing = db.query(AnalysisResult)\
        .filter(AnalysisResult.phishing == True)\
        .count()

    safe = total - phishing

    return {
        "total": total,
        "phishing": phishing,
        "safe": safe
    }


@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    user = Depends(admin_required)
):

    history = db.query(AnalysisResult)\
        .order_by(AnalysisResult.created_at.desc())\
        .all()

    return history


# =========================
# USUARIOS PENDIENTES
# =========================
@router.get("/pending-users")
def get_pending_users(
    db: Session = Depends(get_db),
    user = Depends(admin_required)
):

    users = db.query(User).filter(User.is_approved == False).all()

    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "auth_provider": u.auth_provider,
            "created_at": u.created_at
        }
        for u in users
    ]


# =========================
# APROBAR USUARIO
# =========================
@router.put("/approve-user/{user_id}")
async def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    user = Depends(admin_required)
):

    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_user.is_approved = True
    db.commit()

    try:
        await send_approval_email(db_user.email)
    except Exception as e:
        print("ERROR ENVIANDO CORREO:", e)

    return {"message": "Usuario aprobado correctamente"}
