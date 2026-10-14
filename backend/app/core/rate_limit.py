import time

from fastapi import HTTPException, status

from app.core.dependencies import CurrentUser


class RateLimiter:

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[int, tuple[float, int]] = {}

    async def __call__(self, user: CurrentUser) -> None:
        now = time.monotonic()
        window_start, count = self._hits.get(user.id, (now, 0))

        if now - window_start >= self.window_seconds:
            window_start, count = now, 0

        if count >= self.max_requests:
            retry_after = int(self.window_seconds - (now - window_start)) + 1
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Too many requests",
                headers={"Retry-After": str(retry_after)},
            )

        self._hits[user.id] = (window_start, count + 1)