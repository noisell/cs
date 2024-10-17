# import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.user.router import router as user_router
from src.auth.router import router as auth_router

# sentry_sdk.init(
#     dsn="https://a6419d29a316911c0975d5a7e8bf1576@o4507866867367936.ingest.de.sentry.io/4507866901184592",
#     traces_sample_rate=1.0,
#     profiles_sample_rate=1.0,
# )
app = FastAPI(
    title="CS",
    version="0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://two-market.ru"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS", "DELETE", "PUT"],
    allow_headers=['Access-Control-Allow-Headers', 'Access-Control-Allow-Credentials', 'Content-Type', 'Authorization',
                   'Access-Control-Allow-Origin', 'Cookie', 'Set-Cookie'],
)

app.include_router(user_router)
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
