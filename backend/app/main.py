from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, repo, analysis
from app.database import init_db

app = FastAPI(title="Codebase Analyzer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(repo.router, prefix="/repo", tags=["Repository"])
app.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
