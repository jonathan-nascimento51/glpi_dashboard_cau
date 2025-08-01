from __future__ import annotations

import logging
import os
import ssl
from typing import Optional, Union

import aiohttp
from pydantic import BaseModel, ConfigDict, Field, model_validator

logger = logging.getLogger(__name__)


class Credentials(BaseModel):
    """Authentication data for the GLPI REST API."""

    app_token: str = Field(..., description="GLPI application token")
    user_token: Optional[str] = Field(
        default=None, description="Optional user API token"
    )
    username: Optional[str] = Field(
        default=None, description="GLPI username used when no token is provided"
    )
    password: Optional[str] = Field(
        default=None,
        description="GLPI password used together with ``username``",
    )

    @model_validator(mode="after")
    def _check_auth(self) -> "Credentials":
        """Ensure at least one authentication method is supplied."""
        auth_methods = sum(
            [1 if self.user_token else 0, 1 if (self.username and self.password) else 0]
        )
        if auth_methods == 0:
            raise ValueError("Either user_token or username/password must be provided.")
        if auth_methods > 1:
            logger.debug(
                "Both user_token and username/password provided. "
                "Prioritizing user_token."
            )
            self.username = None
            self.password = None
        return self


class SessionParams(BaseModel):
    """Input data for creating :class:`GLPISession`."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    base_url: str = Field(..., description="GLPI REST base URL")
    credentials: Credentials
    proxy: Optional[str] = Field(
        default_factory=lambda: os.environ.get("HTTP_PROXY"),
        description="Optional proxy URL; defaults to HTTP_PROXY env var",
    )
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    ssl_context: Optional[ssl.SSLContext] = Field(
        default=None, description="Custom SSL context for TLS connections", exclude=True
    )
    timeout: Union[int, aiohttp.ClientTimeout] = Field(
        default=300, description="Request timeout in seconds", exclude=True
    )
    refresh_interval: int = Field(
        default=3000,
        description="Interval in seconds to proactively refresh the session",
    )
