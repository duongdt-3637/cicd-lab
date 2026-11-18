from conf.config import RUNTIME_ENV


class HealthCheckApi:
    def on_get(self, req, resp):
        resp["body"] = {"status": "ok", "env": RUNTIME_ENV}
        return resp
