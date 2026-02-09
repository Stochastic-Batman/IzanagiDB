import asyncio
import logging
from contextlib import asynccontextmanager
from database import Base, document_contents, engine, mongo_client
from fastapi import FastAPI
from routes.auth import router as auth_router


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Wait for PostgreSQL to be ready
    max_retries = 5
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection failed, retrying... ({attempt + 1}/{max_retries}): {e}")
                await asyncio.sleep(2)
            else:
                logger.error("Failed to connect to database after all retries")
                raise
    yield
    await engine.dispose()
    mongo_client.close()


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
