class AppError(Exception):
    def __init__(self, reason: str, status_code: int) -> None:
        self.reason = reason
        self.status_code = status_code
        super().__init__(reason)


class RuleError(AppError):
    """Business-rule rejection. remaining_seconds is set for BR-03."""

    def __init__(self, reason: str, rule: str, remaining_seconds: int | None = None) -> None:
        self.rule = rule
        self.remaining_seconds = remaining_seconds
        super().__init__(reason, 422)

    def detail(self) -> dict[str, str | int | None]:
        return {
            "reason": self.reason,
            "rule": self.rule,
            "remaining_seconds": self.remaining_seconds,
        }


class NotFound(AppError):
    def __init__(self, reason: str) -> None:
        super().__init__(reason, 404)


class Conflict(AppError):
    def __init__(self, reason: str) -> None:
        super().__init__(reason, 409)
