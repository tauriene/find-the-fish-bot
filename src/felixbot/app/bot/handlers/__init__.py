from .user import router as user_router
from .game import router as game_router

routers = (game_router, user_router)
