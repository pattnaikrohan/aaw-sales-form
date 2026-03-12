from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import speech, chat, company, submit, auth, extract_fields
from services.company_search import load_company_cache

app = FastAPI(title="AAW Group Sales App API", version="1.0.0")

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "https://lemon-coast-04dd91300.6.azurestaticapps.net",
    "https://*.azurestaticapps.net"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(speech.router, prefix="/api", tags=["Speech"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(company.router, prefix="/api", tags=["Company"])
app.include_router(submit.router, prefix="/api", tags=["Submit"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(extract_fields.router, prefix="/api", tags=["Extract"])


@app.on_event("startup")
async def startup():
    """Load company names from Dataverse into memory on startup."""
    await load_company_cache()


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": "AAW Group Sales App"}

