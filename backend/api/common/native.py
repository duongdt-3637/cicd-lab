import os
import subprocess

from error.error_handling import ApiError
from logger.logger import get_logger

# Mô phỏng native/tesac của dự án thật: file cần quyền chạy (100755 trong git)
_NATIVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "native")
NATIVE_HELLO_PATH = os.path.join(_NATIVE_DIR, "hello")


def run_native_hello(name):
    try:
        result = subprocess.run(
            [NATIVE_HELLO_PATH, name],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
    except PermissionError as err:
        get_logger().exception("native/hello is not executable")
        raise ApiError(500, "native/hello is not executable") from err
    return result.stdout.strip()


class NativeHelloApi:
    def on_get(self, req, resp):
        resp["body"] = {"output": run_native_hello(req["query"].get("name", "world"))}
        return resp
