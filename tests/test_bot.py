import pytest
import pytest_asyncio
from aiogram.types import Message
from bot import start
from unittest.mock import AsyncMock, MagicMock

@pytest_asyncio.fixture
async def mock_message():
    message = AsyncMock(spec=Message)
    message.from_user = MagicMock()
    message.from_user.full_name = 'test user'
    message.answer = AsyncMock()
    return message

@pytest.mark.asyncio
async def test_start(mock_message):
    await start(mock_message)
    expected_text = (
        "Вітаю, test user!\n"
        "шукай і редагуй фільми на свій смак! Щоб почати, скористайся командами з меню нижче.."
    )
    mock_message.answer.assert_called_once_with(expected_text)
