import json

from api_route import ApiRoute
from error.error_handling import ApiError, MethodNotAllowedError, NotFoundError
from logger.logger import get_logger, init_logger


def lambda_handler(event, context):
    """
    Main handling request from API Gateway (REST API, proxy integration)
    """
    req = _extract_request_info(event)
    init_logger(_extract_access_info(event, context))
    logger = get_logger()

    try:
        api_class = ApiRoute.get_instance(req)
        if api_class is None:
            raise NotFoundError
        handler = getattr(api_class(), f"on_{req['method'].lower()}", None)
        if handler is None:
            raise MethodNotAllowedError
        resp = handler(req, {"statusCode": 200})
    except ApiError as err:
        resp = {"statusCode": err.status_code, "body": {"message": err.message}}
    except Exception:
        logger.exception("unhandled error")
        resp = {"statusCode": 500, "body": {"message": "Internal Server Error"}}

    logger.info("access", extra={"details": {"status": resp["statusCode"]}})
    return _to_api_gateway_response(resp)


def _extract_request_info(event):
    body = event.get("body")
    try:
        body = json.loads(body) if body else {}
    except ValueError:
        body = {}
    return {
        "method": event.get("httpMethod", ""),
        "path": event.get("path", ""),
        "query": event.get("queryStringParameters") or {},
        "body": body,
    }


def _extract_access_info(event, context):
    return {
        "request_id": getattr(context, "aws_request_id", None),
        "method": event.get("httpMethod"),
        "path": event.get("path"),
    }


def _to_api_gateway_response(resp):
    return {
        "statusCode": resp["statusCode"],
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(resp.get("body", {}), ensure_ascii=False),
    }
