"""API v1 路由"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.tenants import router as tenants_router
from app.api.v1.roles import router as roles_router


router = APIRouter()

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(tenants_router)
router.include_router(roles_router)