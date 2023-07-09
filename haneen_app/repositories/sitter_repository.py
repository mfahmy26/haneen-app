from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from haneen_app.database.cruds import get_by

from haneen_app.entities.sitter import Sitter


async def get_sitters(session: AsyncSession) -> List[Sitter]:
    return await get_by(session, Sitter)