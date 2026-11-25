import json

import pytest

from lambda_function import lambda_handler


def _event(path, method="GET", query=None):
    return {"httpMethod": method, "path": path, "queryStringParameters": query, "body": None}


def _call(event):
    resp = lambda_handler(event, None)
    return resp["statusCode"], json.loads(resp["body"])


def test_health_check():
    status, body = _call(_event("/api/health_check"))
    assert status == 200
    assert body["status"] == "ok"
    assert body["deployed_by"] == "codebuild-webhook"


def test_hello_default_name():
    status, body = _call(_event("/api/hello"))
    assert status == 200
    assert body["message"].endswith(", world!")


def test_hello_with_name():
    _, body = _call(_event("/api/hello", query={"name": "Duong"}))
    assert body["message"].endswith(", Duong!")


def test_native_hello():
    status, body = _call(_event("/api/native/hello", query={"name": "lab"}))
    assert status == 200
    assert body["output"] == "hello from native: lab"


def test_not_found():
    status, _ = _call(_event("/api/unknown"))
    assert status == 404


@pytest.mark.parametrize("method", ["POST", "DELETE"])
def test_method_not_allowed(method):
    status, _ = _call(_event("/api/hello", method=method))
    assert status == 405
