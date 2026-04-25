# Oh My Copilot — Free GitHub Copilot proxy for personal LLM providers

Free GitHub Copilot proxy for personal LLM providers. Supports OpenAI, Anthropic (Claude), Gemini, and DeepSeek via One API / New API.

---

## Introduction

Oh My Copilot is a lightweight proxy that lets you route GitHub Copilot requests to your chosen LLM provider (GPT-4, Claude 3.5, DeepSeek, Gemini, etc.) via One API or provider-specific New API endpoints. It is optimized for local and cloud deployment, low latency, and developer workflows (works with the VS Code Copilot extension).

## Key Features

- Multi-provider support: OpenAI, Anthropic (Claude), Gemini, DeepSeek (via One API / New API).
- Easy deployment: Docker image and docker-compose examples included.
- Low latency: connection pooling and minimal proxy overhead.
- VS Code Copilot compatible: acts as a transparent Copilot proxy/gateway.
- Configurable: environment variables to select provider, keys, and tuning options.

## Tech Stack

- Golang (proxy core)
- Docker (containerized deployment)
- One-API / New API (provider gateway)
- Optional: Python helpers and Node.js adapters

## Quick Start

Start a ready-to-run Docker container (example):

```bash
# Example: run using One API / OpenAI provider
docker run -d --name oh-my-copilot \
  -p 8080:8080 \
  -e PROVIDER=openai \
  -e ONE_API_KEY="$ONE_API_KEY" \
  -e PORT=8080 \
  jimmi2051/oh-my-copilot:latest

# Point VS Code Copilot to: http://localhost:8080
```

Using docker-compose:

```yaml
version: "3.8"
services:
  oh-my-copilot:
    image: jimmi2051/oh-my-copilot:latest
    ports:
      - "8080:8080"
    environment:
      - PROVIDER=openai
      - ONE_API_KEY=${ONE_API_KEY}
```

## Configuration

Environment variables:
- PROVIDER — openai | anthropic | gemini | deepseek
- ONE_API_KEY / NEW_API_KEY — gateway API key
- PORT — service port (default: 8080)

## Contributing

See CONTRIBUTING.md. Contributions welcome — open an issue or PR.

## SEO & Topics (suggested)

Keywords: GitHub Copilot proxy, copilot-free, llm-gateway, deepseek, anthropic-claude

Topics: github-copilot-proxy, copilot-free, llm-gateway, deepseek, anthropic-claude

## Links

- Website: https://oh-my-copilot-show-case.vercel.app/
- Docs: docs/

## License

This project is licensed under the MIT License. See LICENSE for details.

