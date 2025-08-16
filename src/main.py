import folium
from de.de import add_de_warnings

from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.requests import Request
from starlette.routing import Route

async def index(request: Request):
    return HTMLResponse("<h1>1337</h1>")

async def api_de(request: Request):
    # make it all async (sync request is slow)
    m = folium.Map(location=[51.0, 10.0], zoom_start=6)
    add_de_warnings(m)
    return JSONResponse(m.to_dict())

app = Starlette(debug=True, routes=[
    Route('/', index),
    Route('/data/de', api_de)
])
