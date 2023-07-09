import uvicorn
from haneen_app.database.cruds import get_by
from haneen_app.database.data_store import get_async_session
from fastapi import Depends, FastAPI
from haneen_app.endpoints import home
from haneen_app.endpoints.v0.root import v0_root
from haneen_app.entities.parent import Parent
from haneen_app.entities.sitter import Sitter
from haneen_app.repositories.sitter_repository import get_sitters
from haneen_app.repositories.parent_repository import get_parents
from starlette.requests import Request


APP_ENDPOINTS = [home.endpoint, v0_root]

def create_app():
    app = FastAPI(title="Haneen App", description="Haneen App Description")
    configure_routers(app)
    # async with get_async_session() as async_session:
    #     # query = text('SELECT firstName, lastName, username FROM tblSitter')
    #     # sitters = await session.execute(select(Sitter))
    #     sitters = await get_sitters(async_session)
    #     parents = await get_parents(async_session)
    #     return {"sitters": sitters, "parents": parents}

    return app


def configure_routers(app: FastAPI) -> None:
    for endpoint in APP_ENDPOINTS:
        app.include_router(
            router=endpoint.router, prefix=endpoint.prefix, dependencies=[Depends(request_body_logging)]
        )


async def request_body_logging(request: Request) -> None:
    request_url = request.url.path
    if request_url != "/":
        request_content = (await request.body()).decode() if request.method == "POST" else request.query_params



if __name__ == "__main__":
    uvicorn.run(
        "start.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["haneen_app"]
    )