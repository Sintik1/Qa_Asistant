"""Application errors mapped to HTTP status + TZ error codes."""

from __future__ import annotations

from dataclasses import dataclass

from core.messages import ERROR_MESSAGES


@dataclass(eq=False)
class AppError(Exception):
    code: str
    status_code: int = 400
    message: str | None = None

    def __post_init__(self) -> None:
        if self.message is None:
            self.message = ERROR_MESSAGES.get(self.code, ERROR_MESSAGES["INTERNAL_ERROR"])
        super().__init__(self.message)

    def to_dict(self) -> dict[str, dict[str, str]]:
        return {"error": {"code": self.code, "message": self.message or ""}}


class NotFoundError(AppError):
    def __init__(self, code: str = "NOT_FOUND") -> None:
        super().__init__(code=code, status_code=404)


class UnauthorizedError(AppError):
    def __init__(self, code: str = "UNAUTHORIZED") -> None:
        super().__init__(code=code, status_code=401)


class ForbiddenError(AppError):
    def __init__(self, code: str = "FORBIDDEN") -> None:
        super().__init__(code=code, status_code=403)


class ValidationError(AppError):
    def __init__(self, code: str = "VALIDATION_ERROR", message: str | None = None) -> None:
        super().__init__(code=code, status_code=422, message=message)
