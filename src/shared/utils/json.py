from typing import Any

from fastapi.responses import JSONResponse


class UTF8JSONResponse(JSONResponse):
    """
    Custom JSONResponse that explicitly sets the charset to UTF-8 in the
    Content-Type header.
    """

    def __init__(self, content: Any, **kwargs: Any):
        kwargs.setdefault("media_type", "application/json; charset=utf-8")
        super().__init__(content, **kwargs)
