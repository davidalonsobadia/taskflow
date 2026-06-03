from fastapi import APIRouter
from app.api.health import router as health_router
from app.domains.auth.router import router as auth_router
from app.domains.lists.router import router as lists_router
from app.domains.tasks.router import router as tasks_router


router = APIRouter(prefix="/api/v1")
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(lists_router)
router.include_router(tasks_router)
