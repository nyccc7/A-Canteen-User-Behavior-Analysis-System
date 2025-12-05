from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import db
from routers import portal, recommend, admin, student

app = FastAPI(title="Cafeteria System API")

# CORS Configuration
origins = [
    "http://localhost:5173", # Vue frontend
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await db.connect_db()

@app.on_event("shutdown")
async def shutdown():
    await db.close_db()

app.include_router(portal.router, prefix="/api/portal", tags=["Portal"])
app.include_router(recommend.router, prefix="/api/recommend", tags=["Recommend"])
app.include_router(student.router, prefix="/api/student", tags=["Student"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {"message": "Welcome to Distributed Cafeteria System API"}


