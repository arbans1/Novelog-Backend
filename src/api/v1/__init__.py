"""API v1"""
from fastapi import APIRouter

from src.api.v1 import auth, users

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
