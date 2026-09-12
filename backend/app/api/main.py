from fastapi import APIRouter

from app.api.routes import locations, work_orders

api_router = APIRouter()
api_router.include_router(locations.router)
api_router.include_router(work_orders.router)