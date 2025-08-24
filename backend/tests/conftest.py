"""
This file contains the conftest for the API.
"""

# 1st party imports
import os
import sys
from typing import Callable
from contextlib import contextmanager

# add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 3rd party imports
import pytest
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session

# local imports
from main import APP
from database.models import Base
from database.database import api_get_session


@pytest.fixture(scope="class")
def engine():
    """
    This function is used to create a test database.
    This function creates a in memory sqlite database for testing.

    Returns:
        sessionmaker: A sessionmaker object.
    """

    # create a in memory database
    test_db = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    # create all the tables
    Base.metadata.create_all(bind=test_db)

    # return the engine
    yield test_db

    # dispose the engine
    test_db.dispose()


@pytest.fixture(scope="class")
def get_test_db(engine: Engine):
    """
    This function is used to get a test database session.
    This function creates a in memory sqlite database for testing.

    Args:
        create_test_db (sessionmaker): A sessionmaker object which is created by the create_test_db fixture.

    Returns:
        Callable: A callable that returns a session object.
    """

    # create a session factory
    test_session_factory = sessionmaker(bind=engine)

    # create a session
    test_session = test_session_factory()

    def __get_session() -> Session:
        """
        This function is used to get a test database session.
        This function is called in the place if the api_get_session fixture.

        Returns:
            Session: A session object.
        """
        try:
            yield test_session
        finally:
            test_session.close()

    return __get_session


@pytest.fixture(scope="class")
def client(get_test_db: Callable[[], Session]):
    """
    This fixture is used to create a test client for the API.
    """

    # override the api_get_session dependency
    APP.dependency_overrides[api_get_session] = get_test_db

    # yield the client
    yield TestClient(APP)

    # remove the override
    APP.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def monkey_patch_get_sync_session(monkeypatch: pytest.MonkeyPatch, get_test_db: Callable[[], Session]):
    """
    This function is used to monkey patch the get_sync_session function.
    The function is used all over the repo to get a session for the database.

    Args:
        monkeypatch (pytest.MonkeyPatch): The monkeypatch object.
        get_test_db (Callable[[], Session]): The get_test_db fixture.

    Returns:
        None
    """

    # create a sync session yielding function
    @contextmanager
    def fake_get_sync_session():
        """
        Create a sync session yielding function.
        This function is used to create a sync session for the database.
        """

        # get the session factory
        get_session_gen = get_test_db()

        # create a session
        session = next(get_session_gen)

        # yield the session
        yield session

    # patch where it's used
    monkeypatch.setattr("wizard.wizard.get_sync_session", fake_get_sync_session, raising=True)
