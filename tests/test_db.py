from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models import User


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
    }
