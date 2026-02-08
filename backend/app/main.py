from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import Base, document_contents, engine, mongo_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create PostgreSQL tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup on shutdown
    await engine.dispose()
    mongo_client.close()


app = FastAPI(lifespan=lifespan)
