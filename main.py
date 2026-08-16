from fastapi import FastAPI

from database import Base, engine
from routers.students import router as student_router
from routers.auth import router as auth_router

app = FastAPI()


# Create database tables
Base.metadata.create_all(bind=engine)


# Register student routes
app.include_router(student_router) # here student_router is alias for router
app.include_router(auth_router)

@app.get("/")
def home():
    return {
        "message": "Student API is running"
    }