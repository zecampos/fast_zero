from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import get_password_hash


@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def client(session):
    def override_get_session():
        return session
    with TestClient(app) as client:
        app.dependency_overrides[get_session] = override_get_session
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:",
                           connect_args={'check_same_thread': False},
                           poolclass=StaticPool)
    table_registry.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    password = 'testtest'
    user = User(username='Teste', email='teste@test.com',
                password=get_password_hash(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    user.clear_password = password
    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clear_password},
    )
    return response.json()['access_token']
