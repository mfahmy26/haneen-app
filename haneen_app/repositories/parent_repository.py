from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from haneen_app.database.cruds import get_by
from haneen_app.entities.parent import Parent


async def get_parents(session: AsyncSession) -> List[Parent]:
    return await get_by(session, Parent)