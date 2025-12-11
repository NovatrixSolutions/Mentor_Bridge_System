from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from . import models
from .routers import email as email_router
from .routers import alumni as alumni_router

# Routers
from .routers import students as students_router
from .routers import recommend as recommend_router
from .routers import feedback as feedback_router
from .routers import connections as connections_router
from .routers import chat as chat_router

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Alumni Recommendation Backend")

# ✅ CORS – ADD YOUR ACTUAL FRONTEND URL
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://mentor-bridge-frontend-kekd.onrender.com",  # ← YOUR ACTUAL URL!
    "*"  # Allow all temporarily for testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(alumni_router.router)
app.include_router(students_router.router)
app.include_router(recommend_router.router)
app.include_router(feedback_router.router)
app.include_router(connections_router.router)
app.include_router(chat_router.router)
app.include_router(email_router.router)

@app.get("/")
def home():
    return {"message": "Backend working successfully 🚀"}
