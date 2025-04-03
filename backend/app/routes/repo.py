from app.routes.llm_tasks import analyze_code_with_llm, generate_suggestion_with_llm
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from datetime import datetime, timezone
from app.database import get_db
from app.models import Analysis, Repository, Suggestion
from app.config import redis_client, SECRET_KEY, ALGORITHM
from pydantic import BaseModel
import jwt
import os
import git
import shutil

router = APIRouter()

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class RepoSubmitRequest(BaseModel):
    repo_url: str

# Function to decode JWT and get user_id
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: user ID not found")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def extract_methods(code: str, file_extension: str) -> list[str]:
    """Extract method/function names based on file type (basic implementation)."""
    methods = []
    code_lines = code.splitlines()
    
    if file_extension == ".py":  # Python
        for line in code_lines:
            line = line.strip()
            if line.startswith("def ") and "(" in line:
                method_name = line.split("def ")[1].split("(")[0].strip()
                methods.append(method_name)
    elif file_extension == ".java":  # Java
        for line in code_lines:
            line = line.strip()
            if ("public" in line or "private" in line or "protected" in line) and "(" in line and "{" in line:
                parts = line.split("(")[0].split()
                if len(parts) > 1:
                    method_name = parts[-1]
                    methods.append(method_name)
    elif file_extension == ".js":  # JavaScript
        for line in code_lines:
            line = line.strip()
            if line.startswith("function ") and "(" in line:
                method_name = line.split("function ")[1].split("(")[0].strip()
                methods.append(method_name)
    # Add more languages as needed (e.g., .cpp, .go)
    return methods

def analyze_repository(repo_id: str, repo_url: str, user_id: str, db: Session):
# Check if recently processed
    last_processed = redis_client.get(f"repo:{repo_id}")
    if last_processed and (datetime.now(timezone.utc) - datetime.fromisoformat(last_processed.decode('utf-8'))).seconds < 600:
        return
    
    repo = db.exec(select(Repository).where(Repository.id == repo_id)).first()
    if not repo:
        repo = Repository(id=repo_id, repo_url=repo_url, user_id=user_id, summary=None)  # No summary yet
        db.add(repo)
        db.commit()
    # Temporary directory for cloning
    clone_dir = f"/tmp/repo_{repo_id}"
    os.makedirs(clone_dir, exist_ok=True)

    try:
        # Clone the repository
        git.Repo.clone_from(repo_url, clone_dir)

        # Local storage for file descriptions and suggestions
        file_analysis: dict[str, dict] = {}

        # Walk through the repository files
        for root, _, files in os.walk(clone_dir):
            for file_name in files:
                # Support multiple languages by checking common extensions
                if file_name.endswith((".py", ".java", ".js", ".cpp", ".go")):  # Add more as needed
                    file_path = os.path.join(root, file_name)
                    file_extension = os.path.splitext(file_name)[1]
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()

                    # Extract method names based on language
                    methods = extract_methods(code, file_extension)
                    if not methods:
                        continue  # Skip files with no methods

                    # Analyze code with LLM
                    analysis_response = analyze_code_with_llm(code, methods, file_extension)
                    file_description = analysis_response.file_description  # Extract file-level description
                    method_details = analysis_response.methods  # Extract method-level details
                    # Store file-level analysis locally
                    file_analysis[file_name] = {
                        "description": file_description,
                        "methods": method_details,
                        "suggestions": []
                    }
                    print(file_analysis[file_name])
                    # Store method analysis in Analysis table
                    for method_name, details in method_details.items():
                        analysis = Analysis(
                            repo_id=repo_id,
                            user_id=user_id,
                            method_name=method_name,
                            description=details.description,
                            time_complexity=details.time_complexity,
                            space_complexity=details.space_complexity
                        )
                        db.add(analysis)
                        db.commit()
                        db.refresh(analysis)

                        # Generate and store suggestion
                        suggestion_text = generate_suggestion_with_llm(method_name, details, code)
                        suggestion = Suggestion(
                            repo_id=repo_id,
                            user_id=user_id,
                            analysis_id=analysis.id,
                            suggestion=suggestion_text
                        )
                        db.add(suggestion)
                        file_analysis[file_name]["suggestions"].append(suggestion_text)

                    db.commit()

        # Generate overall summary
        # overall_summary = generate_overall_summary_with_llm(file_analysis)
        overall_summary = "overall_summary"
        
        # Update or create Repository entry
        repo = db.exec(select(Repository).where(Repository.id == repo_id)).first()
        if repo:
            repo.summary = overall_summary
        db.commit()

        # Update Redis
        redis_client.set(f"repo:{repo_id}", datetime.now(timezone.utc).isoformat())

    finally:
        # Clean up cloned repo
        if os.path.exists(clone_dir):
            shutil.rmtree(clone_dir)

@router.post("/submit_repo")
def submit_repo(
    request: RepoSubmitRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo_id = str(hash(request.repo_url))
    background_tasks.add_task(analyze_repository, repo_id, request.repo_url, user_id, db)
    return {"message": "Repository analysis started!", "repo_id": repo_id}