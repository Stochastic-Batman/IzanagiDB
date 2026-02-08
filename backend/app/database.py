from config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


POSTGRESQL_URL = f"postgresql+psycopg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
MONGODB_URL = f"mongodb://{settings.MONGO_HOST}:{settings.MONGO_PORT}"

engine = create_async_engine(POSTGRESQL_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

mongo_client = AsyncIOMotorClient(MONGODB_URL)
mongo_db = mongo_client["izanagi_warehouse"]
document_contents = mongo_db["document_contents"]


class Base(DeclarativeBase):
    pass


# apparently, dependency for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
