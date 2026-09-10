# backend/app/main.py
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.db import create_db_and_tables
from app.api.routes import work_orders

app = FastAPI(title=settings.PROJECT_NAME)

create_db_and_tables()
app.include_router(work_orders.router)


@app.exception_handler(RequestValidationError)
async def validation_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


@app.get("/ping")
def ping():
    return {"status": "ok"}