import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Base, engine
from routes import auth, group, dm, global_chat
from websocket import gateway
from consumers.redis import consume_events


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    task = asyncio.create_task(consume_events())

    try:
        yield

    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(group.router)
app.include_router(dm.router)
app.include_router(global_chat.router)
app.include_router(gateway.router)


@app.get("/")
def root():
    return {
        "status": "Chat backend running"
    }