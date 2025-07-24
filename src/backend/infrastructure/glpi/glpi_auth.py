from __future__ import annotations

import json
import logging
import os
from typing import Optional

import redis
import requests
from backend.core.settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_TTL_SECONDS,
)
from requests.auth import HTTPBasicAuth
from shared.utils.logging import get_logger
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_fixed,
)

logger = get_logger(__name__)


class GLPIAuthError(Exception):
    """Raised when authentication fails permanently."""


class TemporaryAuthError(Exception):
    """Raised for transient errors that should trigger a retry."""


def _wait_strategy():
    if os.getenv("DISABLE_RETRY_BACKOFF"):
        return wait_fixed(0)
    return wait_exponential(multiplier=1, min=1, max=10)


class GLPIAuthClient:
    """Simple authentication manager for the GLPI REST API."""

    _instance: Optional["GLPIAuthClient"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        base_url: str = GLPI_BASE_URL,
        app_token: str = GLPI_APP_TOKEN,
        *,
        user_token: Optional[str] = GLPI_USER_TOKEN,
        username: Optional[str] = GLPI_USERNAME,
        password: Optional[str] = GLPI_PASSWORD,
        redis_conn: Optional[redis.Redis] = None,
        session: Optional[requests.Session] = None,
        redis_key: str = "glpi:session_token",
        ttl_seconds: int = REDIS_TTL_SECONDS,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.app_token = app_token
        self.user_token = user_token
        self.username = username
        self.password = password
        self.redis_key = redis_key
        self.ttl_seconds = ttl_seconds
        self.session = session or requests.Session()
        self.redis = redis_conn or redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
        )

    @retry(
        stop=stop_after_attempt(5),
        wait=_wait_strategy(),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        retry=retry_if_exception_type(TemporaryAuthError),
        reraise=True,
    )
    def init_session(self) -> str:
        """Authenticate with GLPI and return a new ``session_token``."""

        headers = {"App-Token": self.app_token, "Content-Type": "application/json"}
        auth = None
        if self.user_token:
            headers["Authorization"] = f"user_token {self.user_token}"
            logger.info(json.dumps({"event": "init_session", "method": "user_token"}))
        elif self.username and self.password:
            auth = HTTPBasicAuth(self.username, self.password)
            logger.info(json.dumps({"event": "init_session", "method": "basic_auth"}))
        else:
            raise GLPIAuthError("missing credentials")

        url = f"{self.base_url}/initSession"
        try:
            resp = self.session.get(url, headers=headers, auth=auth, timeout=30)
        except requests.RequestException as exc:
            logger.warning(
                json.dumps({"event": "init_session_error", "error": str(exc)})
            )
            raise TemporaryAuthError from exc

        if resp.status_code == 401:
            logger.error(json.dumps({"event": "unauthorized"}))
            raise GLPIAuthError("unauthorized")
        if resp.status_code >= 500:
            logger.warning(
                json.dumps({"event": "server_error", "status": resp.status_code})
            )
            raise TemporaryAuthError(f"status {resp.status_code}")
        resp.raise_for_status()
        token = resp.json().get("session_token")
        if not token:
            raise GLPIAuthError("session_token missing")
        logger.info(json.dumps({"event": "init_session_success"}))
        return token

    def get_session_token(self, force_refresh: bool = False) -> str:
        """Return a cached ``session_token`` or authenticate if needed."""

        if not force_refresh:
            try:
                token = self.redis.get(self.redis_key)
            except redis.RedisError as exc:  # pragma: no cover - defensive
                logger.warning(json.dumps({"event": "cache_error", "error": str(exc)}))
                token = None
            if token:
                logger.info(json.dumps({"event": "cache_hit"}))
                return token
            logger.info(json.dumps({"event": "cache_miss"}))

        token = self.init_session()
        try:
            self.redis.setex(self.redis_key, self.ttl_seconds, token)
            logger.info(json.dumps({"event": "cache_store", "ttl": self.ttl_seconds}))
        except redis.RedisError as exc:  # pragma: no cover - defensive
            logger.warning(
                json.dumps({"event": "cache_store_error", "error": str(exc)})
            )
        return token
