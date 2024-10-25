from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.skins.service import SkinService
from src.user.router import router as user_router
from src.auth.router import router as auth_router
from src.bets.router import router as bets_router
from src.skins.router import router as skins_router
from src.cases.router import router as cases_router
from src.admin.router import router as admin_router

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://redis_app:6380")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    await SkinService().add_all_skins()
    yield

app = FastAPI(
    title="CS",
    version="0.1",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cs-limited.ru", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS", "DELETE", "PUT"],
    allow_headers=['Access-Control-Allow-Headers', 'Access-Control-Allow-Credentials', 'Content-Type', 'Authorization',
                   'Access-Control-Allow-Origin', 'Cookie', 'Set-Cookie'],
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(bets_router)
app.include_router(skins_router)
app.include_router(cases_router)
app.include_router(admin_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
