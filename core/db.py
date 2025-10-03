from sqlmodel import SQLModel, Session, create_engine
from typing import Generator
from core.config import config


connect_args = {"check_same_thread": False}
engine = create_engine(config.db_connection_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
