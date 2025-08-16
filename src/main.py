from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.requests import Request
from starlette.routing import Route

import importlib
import pkgutil
import api
from decorator import get_registered_routes


async def index(request: Request):
    return HTMLResponse("<h1>1337</h1>")


for loader, module_name, is_pkg in pkgutil.iter_modules(api.__path__):
    importlib.import_module(f"api.{module_name}")

routes = [Route("/", index)] + [
    Route(r["path"], r["handler"]) for r in get_registered_routes()
]
app = Starlette(debug=True, routes=routes)
