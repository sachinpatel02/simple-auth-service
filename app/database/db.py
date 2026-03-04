from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from ..config import settings

# crating async database async_engine, so we can communicate with database using AsyncSession 
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# AsyncSession method creation
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# db & table creation. The method will be called only once at startup of the server
async def create_db_and_tables():
    # importing table models is very important to create the tables
    from .models import User, RefreshToken
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# method to get the session so we can communicate with database
async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            pass

