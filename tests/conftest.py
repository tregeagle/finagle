import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.models import StockTransaction, User  # noqa: F401 — register models
from app.main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def db():
    Base.metadata.create_all(engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestSession(bind=connection)

    # Prevent the session from closing the transaction
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction_inner):
        nonlocal nested
        if transaction_inner.nested and not transaction_inner._parent.nested:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db):
    def _override():
        yield db

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
