from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnalysisResult
from app.auth import get_current_user

router = APIRouter()


@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):

    results = db.query(AnalysisResult).all()

    return results
