from conf.config import APP_MESSAGE


class HelloApi:
    def on_get(self, req, resp):
        name = req["query"].get("name", "world")
        resp["body"] = {"message": f"{APP_MESSAGE}, {name}!"}
        return resp
