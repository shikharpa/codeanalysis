from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_db
from app.models import Repository, Analysis, Suggestion

router = APIRouter()

@router.get("/get_repo/{repo_id}")
def get_repo_analysis(repo_id: str, db: Session = Depends(get_db)):
    repo = db.exec(select(Repository).where(Repository.id == repo_id)).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    analysis = db.exec(select(Analysis).where(Analysis.repo_id == repo_id)).all()
    
    response = {
        "repo_name": repo.summary["name"] if repo.summary else "Unknown",
        "description": repo.summary["description"] if repo.summary else "No description",
        "methods": [
            {"method_name": a.method_name, "description": a.description, 
             "time_complexity": a.time_complexity, "space_complexity": a.space_complexity}
            for a in analysis
        ]
    }
    return response

@router.get("/get_suggestions/{repo_id}/{method_name}")
def get_suggestions(repo_id: str, method_name: str, db: Session = Depends(get_db)):
    analysis = db.exec(select(Analysis).where(Analysis.repo_id == repo_id, Analysis.method_name == method_name)).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Method not found in analysis")

    suggestions = db.exec(select(Suggestion).where(Suggestion.analysis_id == analysis.id)).all()
    
    return {
        "method_name": method_name,
        "suggestions": [s.suggestion for s in suggestions]
    }
