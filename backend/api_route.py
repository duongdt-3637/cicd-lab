from api.common import health_check, hello, native

API_ROUTE = {
    r"/health_check": {"class": health_check.HealthCheckApi},
    r"/hello": {"class": hello.HelloApi},
    r"/native/hello": {"class": native.NativeHelloApi},
}


def _apply_prefix(routes: dict, prefix: str) -> dict:
    return {f"{prefix}{path}": config for path, config in routes.items()}


# REST API Gateway gửi path đầy đủ, vd. "/api/hello"
API_PREFIX = "/api"
API_ROUTE = _apply_prefix(API_ROUTE, API_PREFIX)


class ApiRoute:
    @staticmethod
    def get_instance(req):
        return API_ROUTE.get(req.get("path"), {}).get("class")
