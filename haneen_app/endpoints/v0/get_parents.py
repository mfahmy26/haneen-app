from typing import Any, Dict, List
from haneen_app.database.data_store import yield_async_session
from haneen_app.entities.parent import Parent
from haneen_app.repositories.parent_repository import get_parents as get_all_parents
from haneen_app.endpoints.v0.root import v0_root
from fastapi import status, Depends
from sqlalchemy.ext.asyncio import AsyncSession


@v0_root.router.get(
    "/get_parents/",
    response_model=List,
    status_code=status.HTTP_200_OK,
    summary="Get all the available parents",
    response_description="A list of all parents",
    tags=["Parents"]
)
async def get_parents(session: AsyncSession = Depends(yield_async_session)):
    try:
        parents = await get_all_parents(session)
        print("HERE")
        result = [parent.to_dict() for parent in parents]
        return result
    except Exception as e:
        print(str(e))