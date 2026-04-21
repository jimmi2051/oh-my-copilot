import json
from unittest.mock import patch

from omc_copilot.notifications import WebhookNotifier


def test_send_sync_slack_success():
    notifier = WebhookNotifier("https://example.com/webhook", provider="slack")

    class DummyResp:
        status_code = 200

    with patch("httpx.Client.post", return_value=DummyResp()):
        ok = notifier.send_sync("hello world", tags="<!here>")
        assert ok


def test_send_sync_failure():
    notifier = WebhookNotifier("https://example.com/webhook", provider="discord")

    class DummyResp:
        status_code = 500

    with patch("httpx.Client.post", return_value=DummyResp()):
        ok = notifier.send_sync("hello")
        assert not ok
