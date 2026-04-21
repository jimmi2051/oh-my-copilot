## Notifications and Node/TS bridge (draft)

This repository now includes a lightweight webhook notifier and an optional Node/TS bridge scaffold.

Files added:
- omc_copilot/notifications.py - WebhookNotifier for Slack/Discord/Telegram
- omc_copilot/cli/notify.py - CLI helper for configuring and sending notifications
- .omc/hooks/* - simple wrappers that call the notify CLI
- plugins/omc-copilot/hooks.json - updated to include notification hooks
- docs/NOTIFICATIONS.md - documentation for configuring notifications
- scripts/setup_node_adapter.sh - scaffolding for an optional Node adapter
- omc_copilot/adapters/js_bridge.py - JS bridge adapter (call Node scripts)

Planned follow-ups:
- Harden webhook handling (rate limits, signing, retries)
- Add richer payload formatting and attachments
- Add integration tests using a local HTTP server or request interception
- Prepare PR with changelog and migration notes
