from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.schemas import MessageRequest, EmailRequest
from app.database import get_db
from app.auth import get_current_user
from app.models import AnalysisResult
from app.analyzer import analyze_message
from app.ml.predict import predict_url
from sqlalchemy import func
from datetime import date
from sqlalchemy import func
from app.models import AnalysisResult

from app.auth import get_current_admin
from sqlalchemy import func
from app.models import AnalysisResult, User

from app.auth import admin_required
from app.models import AnalysisResult, User

from typing import List
from app.schemas import UserResponse
from app.ml_service import predict_phishing
from app.schemas import AnalyzeRequest

from fastapi import UploadFile, File
import PyPDF2
import docx
import io



router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)

@router.post("/email")
def analyze_email(data: EmailRequest):
    prediction = predict_url(data.text)
    return {
        "input": data.text,
        "prediction": prediction
    }

@router.post("/message")
def analyze_message_api(
    data: MessageRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    import re
    from app.main import analyze_urls, analyze_urgency, analyze_social_engineering

    # 🔹 Obtener usuario real desde BD
    db_user = db.query(User).filter(
        User.email == current_user["email"]
    ).first()

    text = data.text.strip()

    # 🔹 Modelo español
    prob_es = predict_phishing(text)

    # 🔹 Sistema heurístico
    url_score, url_triggers = analyze_urls(text)
    urgency_score, urgency_triggers = analyze_urgency(text)
    social_score, social_triggers = analyze_social_engineering(text)

    prob_en = min(url_score + urgency_score + social_score, 1.0)
    reasons_list = url_triggers + urgency_triggers + social_triggers

    contains_url = "http://" in text.lower() or "https://" in text.lower()
    domain_match = re.search(r"https?://([^/]+)", text.lower())
    domain = domain_match.group(1) if domain_match else ""

    trusted_domains = [
        "gob.mx", "sat.gob.mx", "bbva.mx",
        "banamex.com", "paypal.com",
        "google.com", "microsoft.com",
        "drive.google.com"
    ]

    is_trusted = any(td in domain for td in trusted_domains)

    if contains_url and prob_en == 0:
        if is_trusted:
            final_prob = prob_es * 0.3
        elif "urgente" not in text.lower() and "suspend" not in text.lower():
            final_prob = prob_es * 0.5
        else:
            final_prob = (0.6 * prob_es) + (0.4 * prob_en)
    else:
        final_prob = (0.6 * prob_es) + (0.4 * prob_en)

    final_prob = min(max(final_prob, 0.0), 1.0)

    is_phishing = final_prob > 0.5

    if final_prob > 0.75:
        risk_level = "HIGH"
    elif final_prob > 0.40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    risk_score = round(final_prob * 100)

    # 🔥 Guardar con user_id
    db_result = AnalysisResult(
        message=text,
        phishing=is_phishing,
        risk_score=risk_score,
        risk_level=risk_level,
        reasons=", ".join(reasons_list) if reasons_list else "Sin factores sospechosos detectados",
        user_id=db_user.id
    )

    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    return {
        "phishing_probability": final_prob,
        "is_phishing": is_phishing,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "created_at": db_result.created_at,
        "reasons": reasons_list
    }



@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_user = db.query(User).filter(
        User.email == current_user["email"]
    ).first()

    if db_user.role == "admin":
        total = db.query(func.count(AnalysisResult.id)).scalar()
        phishing = db.query(func.count(AnalysisResult.id)).filter(
            AnalysisResult.phishing == True
        ).scalar()
    else:
        total = db.query(func.count(AnalysisResult.id)).filter(
            AnalysisResult.user_id == db_user.id
        ).scalar()

        phishing = db.query(func.count(AnalysisResult.id)).filter(
            AnalysisResult.user_id == db_user.id,
            AnalysisResult.phishing == True
        ).scalar()

    legitimate = total - phishing if total else 0
    phishing_rate = round((phishing / total) * 100, 2) if total else 0

    return {
        "total_analysis": total,
        "phishing_detected": phishing,
        "legitimate_detected": legitimate,
        "phishing_rate": phishing_rate
    }
@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_user = db.query(User).filter(
        User.email == current_user["email"]
    ).first()

    if db_user.role == "admin":
        results = db.query(AnalysisResult).order_by(
            AnalysisResult.id.desc()
        ).all()
    else:
        results = db.query(AnalysisResult).filter(
            AnalysisResult.user_id == db_user.id
        ).order_by(AnalysisResult.id.desc()).all()

    return [
        {
            "message": r.message,
            "phishing": r.phishing,
            "risk_score": r.risk_score,
            "risk_level": r.risk_level,
            "reasons": r.reasons
        }
        for r in results
    ]


@router.get("/stats-by-date")
def stats_by_date(
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    results = (
        db.query(
            func.date(AnalysisResult.created_at).label("date"),
            func.count(AnalysisResult.id).label("total")
        )
        .group_by(func.date(AnalysisResult.created_at))
        .order_by(func.date(AnalysisResult.created_at))
        .all()
    )

    return [
        {
            "date": str(r.date),
            "total": r.total
        }
        for r in results
    ]

@router.get("/admin/global-stats")
def global_stats(
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):

    total_users = db.query(User).count()
    total_analysis = db.query(AnalysisResult).count()

    phishing = db.query(AnalysisResult)\
        .filter(AnalysisResult.phishing == True).count()

    return {
        "total_users": total_users,
        "total_analysis": total_analysis,
        "phishing_detected": phishing
    }

@router.get("/admin/all-analysis")
def get_all_analysis(
    db: Session = Depends(get_db),
    user = Depends(admin_required)
):

    results = db.query(AnalysisResult).order_by(AnalysisResult.created_at.desc()).all()

    return results

@router.get("/admin/users", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    user = Depends(admin_required)
):

    users = db.query(User).all()

    return users

@router.delete("/admin/delete-user/{user_id}")
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

@router.get("/admin/global-stats")
def global_stats(
    db: Session = Depends(get_db),
    user = Depends(admin_required)
):

    total = db.query(AnalysisResult).count()

    phishing = db.query(AnalysisResult).filter(AnalysisResult.phishing == True).count()

    legit = db.query(AnalysisResult).filter(AnalysisResult.phishing == False).count()

    return {
        "total": total,
        "phishing": phishing,
        "legit": legit
    }


@router.post("/analyze")
def analyze(data: AnalyzeRequest):

    prob = predict_phishing(data.message)

    return {
        "phishing_probability": prob,
        "is_phishing": prob > 0.5
    }
@router.post("/file")
def analyze_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    import re
    import PyPDF2
    import docx

    # 🔹 Obtener usuario real
    db_user = db.query(User).filter(
        User.email == current_user["email"]
    ).first()

    content = ""

    if file.filename.endswith(".txt"):
        content = file.file.read().decode("utf-8")

    elif file.filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file.file)
        for page in pdf_reader.pages:
            content += page.extract_text() or ""

    elif file.filename.endswith(".docx"):
        doc = docx.Document(file.file)
        for para in doc.paragraphs:
            content += para.text + "\n"

    else:
        raise HTTPException(status_code=400, detail="Formato no soportado")

    content = content.strip()

    if not content:
        raise HTTPException(status_code=400, detail="No se pudo extraer texto")

    word_count = len(content.split())

    prob_es = predict_phishing(content)
    result_en = analyze_message(content)

    triggers = result_en.get("reasons", [])
    prob_en = 0.6 if result_en["phishing"] else 0.0

    final_prob = (0.55 * prob_es) + (0.45 * prob_en)

    if word_count > 1000:
        final_prob *= 0.85
    if word_count > 3000:
        final_prob *= 0.75
    if word_count > 5000:
        final_prob *= 0.65

    final_prob = min(max(final_prob, 0.0), 1.0)

    if final_prob > 0.85:
        risk_level = "HIGH"
        is_phishing = True
    elif final_prob > 0.50:
        risk_level = "MEDIUM"
        is_phishing = False
    else:
        risk_level = "LOW"
        is_phishing = False

    risk_score = round(final_prob * 100)

    db_result = AnalysisResult(
        message=f"[FILE] {file.filename}",
        phishing=is_phishing,
        risk_score=risk_score,
        risk_level=risk_level,
        reasons="Análisis inteligente de archivo",
        user_id=db_user.id
    )

    db.add(db_result)
    db.commit()

    return {
        "filename": file.filename,
        "phishing_probability": final_prob,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "is_phishing": is_phishing
    }


    import re
    from app.main import analyze_urls, analyze_urgency, analyze_social_engineering

    text = data.text.strip()

    # 🔹 Modelo español (BERT)
    prob_es = predict_phishing(text)

    # 🔹 Sistema heurístico avanzado (explicabilidad real)
    url_score, url_triggers = analyze_urls(text)
    urgency_score, urgency_triggers = analyze_urgency(text)
    social_score, social_triggers = analyze_social_engineering(text)

    prob_en = min(url_score + urgency_score + social_score, 1.0)

    reasons_list = url_triggers + urgency_triggers + social_triggers

    # Detectar si contiene URL
    contains_url = "http://" in text.lower() or "https://" in text.lower()

    # Extraer dominio
    domain_match = re.search(r"https?://([^/]+)", text.lower())
    domain = domain_match.group(1) if domain_match else ""

    trusted_domains = [
        "gob.mx",
        "sat.gob.mx",
        "bbva.mx",
        "banamex.com",
        "paypal.com",
        "google.com",
        "microsoft.com",
        "drive.google.com"
    ]

    is_trusted = any(td in domain for td in trusted_domains)

    # 🔥 Lógica híbrida inteligente (igual que ya tenías)

    if contains_url and prob_en == 0:

        if is_trusted:
            final_prob = prob_es * 0.3

        elif "urgente" not in text.lower() and "suspend" not in text.lower():
            final_prob = prob_es * 0.5

        else:
            final_prob = (0.6 * prob_es) + (0.4 * prob_en)

    else:
        final_prob = (0.6 * prob_es) + (0.4 * prob_en)

    final_prob = min(max(final_prob, 0.0), 1.0)

    is_phishing = final_prob > 0.5

    # Nivel de riesgo
    if final_prob > 0.75:
        risk_level = "HIGH"
    elif final_prob > 0.40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    risk_score = round(final_prob * 100)

    print("----- ANALYSIS DEBUG -----")
    print("Texto:", text)
    print("Dominio:", domain)
    print("Es confiable:", is_trusted)
    print("Prob Español:", prob_es)
    print("Prob Heurístico:", prob_en)
    print("Final:", final_prob)
    print("Razones:", reasons_list)
    print("--------------------------")

    db_result = AnalysisResult(
        message=text,
        phishing=is_phishing,
        risk_score=risk_score,
        risk_level=risk_level,
        reasons=", ".join(reasons_list) if reasons_list else "Sin factores sospechosos detectados",
    )

    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    return {
        "phishing_probability": final_prob,
        "is_phishing": is_phishing,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "created_at": db_result.created_at,
        "reasons": reasons_list
    }
