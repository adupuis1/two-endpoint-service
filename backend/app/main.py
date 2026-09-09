# backend/app/main.py
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import settings
from app.db import create_db_and_tables

app = FastAPI(title=settings.PROJECT_NAME)

create_db_and_tables()


@app.exception_handler(RequestValidationError)
async def validation_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": exc.errors()})

@app.get("/ping")
def ping():
    return {"status": "ok"}