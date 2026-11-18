from api.common.hello import HelloApi
from api_route import ApiRoute


def test_route_found():
    assert ApiRoute.get_instance({"method": "GET", "path": "/api/hello"}) is HelloApi


def test_route_not_found():
    assert ApiRoute.get_instance({"method": "GET", "path": "/api/unknown"}) is None


def test_route_requires_prefix():
    assert ApiRoute.get_instance({"method": "GET", "path": "/hello"}) is None
