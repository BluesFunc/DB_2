from fastapi import APIRouter
from .health import router as health_router
from .auth_router import router as auth_router
from .bookings_router import router as bookings_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(bookings_router)