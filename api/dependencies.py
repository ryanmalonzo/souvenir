import logging
import os

from sqlmodel import Session, create_engine

DATABASE_URL = os.environ.get("DATABASE_URL")
SOUVENIR_EMAIL = "hello@souvenir.app"

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
