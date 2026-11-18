class ApiError(Exception):
    def __init__(self, status_code, message):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class NotFoundError(ApiError):
    def __init__(self):
        super().__init__(404, "API not found")


class MethodNotAllowedError(ApiError):
    def __init__(self):
        super().__init__(405, "Method not allowed")
