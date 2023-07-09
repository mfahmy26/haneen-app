from typing import Any, Dict, List
from haneen_app.database.data_store import yield_async_session
from haneen_app.repositories.sitter_repository import get_sitters
from haneen_app.endpoints.v0.root import v0_root
from fastapi import status, Depends
from sqlalchemy.ext.asyncio import AsyncSession


@v0_root.router.get(
    "/get_sitters/",
    response_model=List,
    status_code=status.HTTP_200_OK,
    summary="Get all the available baby sitters",
    response_description="A list of all baby sitters",
    tags=["Sitters"]
)
async def get_baby_sitters(session: AsyncSession = Depends(yield_async_session)):
    
    sitters = await get_sitters(session)
    result =  [sitter.to_dict() for sitter in sitters]
    print(result)
    return result