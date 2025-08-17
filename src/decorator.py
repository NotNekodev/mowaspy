_registry = []

def api_route(path: str):
    def decorator(func):
        _registry.append({"path": path, "handler": func})
        return func

    return decorator

def add_country_api_routes(country_code: str, routes: list):
    for route in routes:
        _registry.append({"path": f"/{country_code}{route['path']}", "handler": route['handler']})

def get_registered_routes():
    return _registry
