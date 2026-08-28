from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.auth.login.router import login_router
from app.modules.auth.change_password.router import change_password_router
from app.core.config import settings

app = FastAPI()

app.include_router(login_router)
app.include_router(change_password_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)