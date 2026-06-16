"""
KYOUKAI Central OS — Claude API 共通クライアント
ANTHROPIC_API_KEY 環境変数から読む。
"""

from __future__ import annotations

import os
import anthropic

MODEL = "claude-haiku-4-5-20251001"

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY が設定されていません")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def ask(system: str, user: str, max_tokens: int = 1024) -> str:
    client = get_client()
    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return message.content[0].text
