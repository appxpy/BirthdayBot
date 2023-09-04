from typing import Optional

from loguru import logger

from bot.models import User


async def create_user(
    user_id: int, full_name: str, username: Optional[str] = None
) -> Optional[User]:
    user = await get_user(user_id)
    if not user:
        user = await User.create(
            user_id=user_id, username=username, full_name=full_name
        )
        logger.info(f"New User: {user}")
    return user


async def get_user(user_id: int) -> Optional[User]:
    return await User.filter(user_id=user_id).first()
