from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.requests import Request
from starlette.routing import Route, WebSocketRoute, Mount
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.staticfiles import StaticFiles

import importlib
import pkgutil
import api
from typing import List
import json
import asyncio
import gzip
import logging

from map import NoctoMap 
from plug import logger_main # in map because circular import stuff

connected_clients: List[WebSocket] = []
map = NoctoMap()

async def index(request: Request):
    with open("src/frontend/frontend.html") as f:
        content = f.read()
    return HTMLResponse(content)

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        alerts = map.get_alerts()
        
        alerts_json = json.dumps(alerts)
        if len(alerts_json) > 1000:
            compressed_data = gzip.compress(alerts_json.encode('utf-8'))
            await websocket.send_bytes(b'gzip:' + compressed_data)
        else:
            await websocket.send_json(alerts)

        while True:
            message = await websocket.receive_text()
            
            if message == "refresh":
                alerts = map.get_alerts()
                alerts_json = json.dumps(alerts)
                
                if len(alerts_json) > 1000:
                    compressed_data = gzip.compress(alerts_json.encode('utf-8'))
                    await websocket.send_bytes(b'gzip:' + compressed_data)
                else:
                    await websocket.send_json(alerts)
                    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger_main.error(f"Error in websocket_endpoint: {e}")
    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)

async def broadcast_alerts():
    """Broadcast alerts to all connected clients"""
    if not connected_clients:
        return

    try:
        alerts = map.get_alerts()
        alerts_json = json.dumps(alerts)
        disconnected = []
        
        use_compression = len(alerts_json) > 1000
        if use_compression:
            compressed_data = gzip.compress(alerts_json.encode('utf-8'))
        for client in connected_clients:
            try:
                if use_compression:
                    await client.send_bytes(b'gzip:' + compressed_data)
                else:
                    await client.send_json(alerts)
            except Exception as e:
                logger_main.error(f"Failed to send to client: {e}")
                disconnected.append(client)

        for client in disconnected:
            if client in connected_clients:
                connected_clients.remove(client)
                
        if disconnected:
            logger_main.error(f"Removed {len(disconnected)} disconnected clients")
            
    except Exception as e:
        logger_main.error(f"Error in broadcast_alerts: {e}")

async def update_alerts_task():
    """Background task to periodically update and broadcast alerts"""
    while True:
        try:
            map.update()
            await broadcast_alerts()
        except Exception as e:
            logger_main.error(f"Error in update_alerts_task: {e}")
        
        await asyncio.sleep(60)

for loader, module_name, is_pkg in pkgutil.iter_modules(api.__path__):
    importlib.import_module(f"api.{module_name}")

routes = [
    Route("/", index), 
    WebSocketRoute("/ws/global_map", websocket_endpoint),
    Mount('/static', StaticFiles(directory="src/frontend/"), name="static")
]

app = Starlette(debug=True, routes=routes)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_alerts_task())