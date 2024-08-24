from sqlmodel import SQLModel, create_engine, Session
from app.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
