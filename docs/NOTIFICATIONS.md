omc-copilot notifications

Overview

omc-copilot includes a webhook notifier to send lifecycle events and alerts to external services such as Slack, Discord, and Telegram. The implementation is Python-first and intended to be easy to configure for repository maintainers and CI.

Quick start

1. Configure a webhook for a provider:

   python -m omc_copilot.cli.notify config set --provider slack --webhook https://hooks.slack.com/services/TOKEN

2. Send a test message:

   python -m omc_copilot.cli.notify send --provider slack --message "Hello from omc-copilot"

Local config

- Configuration is written to .omc/notify_config.json in the current working directory by default.
- Webhook URLs are sensitive: avoid committing them. Use environment variables in CI or repository secrets where appropriate.

Hook wiring

- Example hooks are provided under .omc/hooks/ and plugins/omc-copilot/hooks.json includes reference to notification hooks for SessionEnd and PostToolUseFailure.
- The hooks call the notify CLI to send simple messages. These wrappers are intentionally lightweight and non-blocking.

Tag formatting

- Slack: messages are sent using the 'text' field. Example tag: "<!here>"
- Discord: messages use 'content'. Mentions are raw text tags in the message body.
- Telegram: 'text' is used for compatibility with common webhook adapters.

Security

- Prefer setting webhook URLs via environment variables in CI instead of storing them in repository files.
- Do not paste production secrets into PRs or public issues.

Using Node/TS bridge (optional)

- For teams that already use oh-my-claudecode TypeScript adapters, an optional Node/TS bridge is planned to reuse existing notification scripts. This bridge will be documented separately and is low priority.

Contributing

- Unit tests live in tests/test_notifications.py and mock network calls.
- For larger integrations, create a feature branch and open a PR referencing this docs page.
