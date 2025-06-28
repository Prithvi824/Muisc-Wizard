"""
This is the main file for the database module.
It contains the main function and the main logic for the database module.
"""

# 1st party imports
from typing import Generator
from contextlib import contextmanager

# 3rd party imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# local imports
from config import DB_URL, ECHO_SQL


# Create a SQLAlchemy engine
SQL_ENGINE = create_engine(
    DB_URL,
    echo=ECHO_SQL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    pool_pre_ping=True,
)

# Create a session factory
session_factory = sessionmaker(bind=SQL_ENGINE)

# create a sync session yielding function
@contextmanager
def get_sync_session() -> Generator[Session, None, None]:
    """
    Create a sync session yielding function.
    This function is used to create a sync session for the database.
    """

    # create a session
    session = session_factory()

    try:
        yield session
    finally:
        session.close()

def api_get_session() -> Generator[Session, None, None]:
    """
    This function is used to create a session for the FastAPI application.
    It yields a session to FastAPI during the request and closes it after the request is completed.
    """

    session = session_factory()
    try:
        yield session
    finally:
        session.close()