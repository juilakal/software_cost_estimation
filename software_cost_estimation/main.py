from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.estimator import estimate_using_cocomo, estimate_using_fpa
from backend.auth import (
    hash_password, verify_password, create_access_token, get_current_user
)
from backend.database import (
    init_db, create_user, get_user_by_email,
    save_estimation, get_estimations
)
import os

app = FastAPI()

# ── CORS ────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# ── Startup ─────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    init_db()


# ── Request Models ──────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class CocomoRequest(BaseModel):
    kloc: float
    project_type: str       # "organic" | "semi" | "embedded"
    cost_per_pm: float

class FpaRequest(BaseModel):
    fp: float
    language: str           # "python" | "java" | "c"
    cost_per_pm: float


# ── Auth Endpoints ──────────────────────────────────────────────
@app.post("/auth/register")
def register(data: RegisterRequest):
    if get_user_by_email(data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(data.password)
    try:
        create_user(data.username, data.email, hashed)
    except Exception:
        raise HTTPException(status_code=400, detail="Username already taken")
    return {"message": "Registration successful"}


@app.post("/auth/login")
def login(data: LoginRequest):
    user = get_user_by_email(data.email)
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({
        "user_id": user["id"],
        "email": user["email"],
        "username": user["username"],
    })
    return {"access_token": token, "token_type": "bearer", "username": user["username"]}


# ── PWA Service Worker (must be at root for scope) ──────────────
@app.get("/sw.js")
def service_worker():
    return FileResponse("static/sw.js", media_type="application/javascript")

# ── Serve HTML Pages ────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r") as f:
        return f.read()

@app.get("/login", response_class=HTMLResponse)
def login_page():
    with open("templates/login.html", "r") as f:
        return f.read()

@app.get("/register", response_class=HTMLResponse)
def register_page():
    with open("templates/register.html", "r") as f:
        return f.read()

@app.get("/history", response_class=HTMLResponse)
def history_page():
    with open("templates/history.html", "r") as f:
        return f.read()


# ── COCOMO Endpoint ─────────────────────────────────────────────
@app.post("/estimate/cocomo")
def estimate_cocomo(data: CocomoRequest, user: dict = Depends(get_current_user)):
    effort, time, cost = estimate_using_cocomo(
        data.kloc, data.project_type, data.cost_per_pm
    )
    result = {
        "effort": round(effort, 2),
        "time": round(time, 2),
        "cost": round(cost, 2),
    }
    # Save to history
    save_estimation(
        user_id=user["user_id"],
        method="COCOMO",
        inputs={"kloc": data.kloc, "project_type": data.project_type,
                "cost_per_pm": data.cost_per_pm},
        effort=result["effort"],
        time_val=result["time"],
        cost=result["cost"],
    )
    return result


# ── FPA Endpoint ────────────────────────────────────────────────
@app.post("/estimate/fpa")
def estimate_fpa(data: FpaRequest, user: dict = Depends(get_current_user)):
    effort, time, cost = estimate_using_fpa(
        data.fp, data.language, data.cost_per_pm
    )
    result = {
        "effort": round(effort, 2),
        "time": round(time, 2),
        "cost": round(cost, 2),
    }
    save_estimation(
        user_id=user["user_id"],
        method="FPA",
        inputs={"fp": data.fp, "language": data.language,
                "cost_per_pm": data.cost_per_pm},
        effort=result["effort"],
        time_val=result["time"],
        cost=result["cost"],
    )
    return result


# ── History Endpoint ────────────────────────────────────────────
@app.get("/api/history")
def get_history(user: dict = Depends(get_current_user)):
    records = get_estimations(user["user_id"])
    return {"history": records}