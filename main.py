from fastapi import FastAPI

import handlers
from core.lifespan import lifespan
from handlers.http.handler import router

app = FastAPI(lifespan=lifespan)

app.include_router(router)