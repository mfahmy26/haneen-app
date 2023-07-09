
from haneen_app.endpoints import Endpoint


endpoint = Endpoint(prefix="")

@endpoint.router.get("/")
def read_root():
    return {"hello": "world"}