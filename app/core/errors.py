from dataclasses import dataclass


class AppError(Exception):
    """统一业务异常基类。"""

    code = "APP_ERROR"
    status_code = 500

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    code = "VALIDATION_ERROR"
    status_code = 400


class ProviderError(AppError):
    code = "PROVIDER_ERROR"
    status_code = 502


class FlowError(AppError):
    code = "FLOW_ERROR"
    status_code = 400


@dataclass(frozen=True)
class ErrorResponse:
    code: str
    message: str

