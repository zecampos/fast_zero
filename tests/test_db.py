from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models import Todo, User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(username="alice", email="alice@example.com",
                        password="testpassword")
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == "alice"))
    assert user.username == "alice"
    assert asdict(user) == {
        "id": 1,
        "username": "alice",
        "password": "testpassword",
        "email": "alice@example.com",
        "created_at": time,
        "todos": [],
    }


@pytest.mark.asyncio
async def test_create_todo(session, user):
    todo = Todo(title="Test Todo", description="Test Desc",
                state='draft', user_id=user.id)
    session.add(todo)
    await session.commit()

    todo = await session.scalar(select(Todo))
    assert asdict(todo) == {
        "id": 1,
        "title": "Test Todo",
        "description": "Test Desc",
        "state": "draft",
        "user_id": user.id,
    }


@pytest.mark.asyncio
async def test_user_todo_relationship(session, user: User):
    todo = Todo(title="Test Todo", description="Test Desc",
                state='draft', user_id=user.id)
    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    user = await session.scalar(select(User).where(User.id == user.id))
    assert user.todos == [todo]
