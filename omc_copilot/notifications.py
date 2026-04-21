"""Simple webhook notifier supporting Slack, Discord, and Telegram.

Provides an async send() and a sync wrapper send_sync() suitable for CLI use and tests.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 10


class WebhookNotifier:
    """Send messages to webhook endpoints for common providers.

    Usage:
        n = WebhookNotifier("https://example.com/webhook", provider="slack")
        n.send_sync("hello")
    """

    def __init__(
        self,
        webhook_url: str,
        provider: str = "slack",
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 3,
    ):
        self.webhook_url = webhook_url
        self.provider = (provider or "slack").lower()
        self.timeout = timeout
        self.max_retries = max_retries

    def _build_payload(
        self, message: str, tags: Optional[str] = None
    ) -> Dict[str, Any]:
        text = message
        if tags:
            text = f"{tags} {text}"

        if self.provider == "slack":
            return {"text": text}
        if self.provider == "discord":
            return {"content": text}
        if self.provider == "telegram":
            # Many Telegram webhook endpoints accept a JSON body with 'text'
            return {"text": text}
        return {"text": text}

    async def send(self, message: str, tags: Optional[str] = None) -> bool:
        payload = self._build_payload(message, tags)
        backoff = 1.0
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(self.webhook_url, json=payload)
                status = getattr(resp, "status_code", None)
                if status and 200 <= status < 300:
                    return True
                logger.warning("Notifier attempt %d failed: status=%s", attempt, status)
            except Exception as exc:  # pragma: no cover - network errors
                logger.exception("Notifier attempt %d error: %s", attempt, exc)
            await asyncio.sleep(backoff)
            backoff *= 2
        return False

    def send_sync(self, message: str, tags: Optional[str] = None) -> bool:
        payload = self._build_payload(message, tags)
        backoff = 1.0
        for attempt in range(1, self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(self.webhook_url, json=payload)
                status = getattr(resp, "status_code", None)
                if status and 200 <= status < 300:
                    return True
                logger.warning(
                    "Notifier sync attempt %d failed: status=%s", attempt, status
                )
            except Exception as exc:  # pragma: no cover - network errors
                logger.exception("Notifier sync attempt %d error: %s", attempt, exc)
            time.sleep(backoff)
            backoff *= 2
        return False


__all__ = ["WebhookNotifier"]
