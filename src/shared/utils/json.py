from typing import Any

from fastapi.responses import ORJSONResponse


class UTF8JSONResponse(ORJSONResponse):
    """
    Custom JSONResponse that explicitly sets the charset to UTF-8 in the
    Content-Type header, using the high-performance orjson library.
    """

    def __init__(self, content: Any, status_code: int = 200, **kwargs: Any) -> None:
        """Initialize response with default UTF-8 JSON media type."""
        kwargs.setdefault("media_type", "application/json; charset=utf-8")
        super().__init__(content, status_code=status_code, **kwargs)
