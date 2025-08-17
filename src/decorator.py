_registry = []


def api_route(path: str):
    def decorator(func):
        _registry.append({"path": path, "handler": func})
        return func

    return decorator


def get_registered_routes():
    return _registry
