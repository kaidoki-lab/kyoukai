"""
KYOUKAI Central OS — AI企画官 v1
GA4分析・観測データを受け取り、自由な企画案を生成する。

Ollama接続時  : ローカルAIが企画を生成
Ollama未接続時: 最低限の仮企画を返す
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.error import URLError
from urllib.request import Request as UrlRequest, urlopen

OLLAMA_URL   = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:0.5b"

# ─── フォールバック仮企画 ──────────────────────────────────────────────────────

_FALLBACK_PLANS = [
    {
        "title": "崩落域の記憶断片追加",
        "summary": "/nullに断片化したテキストを追加し、「なにかがあった」という印象を与える。",
        "reason": "崩落域への反応が確認されており、さらなる深みで滞在時間が伸びる可能性がある。",
        "targets": ["/null"],
        "implementationSize": "small",
    },
    {
        "title": "観測域と信号域の隠れた導線",
        "summary": "/observationから/signalへの意図的に薄い接続リンクを追加する。",
        "reason": "両ページとも反応があり、接続することで回遊率が向上する可能性がある。",
        "targets": ["/observation", "/signal"],
        "implementationSize": "small",
    },
    {
        "title": "外部境界テキストの変質",
        "summary": "/outsideの接続テキストを壊れた形式に変更し、境界の異常感を演出する。",
        "reason": "KYOUKAIの世界観強化のため、外部接続を「狂った境界」として演出する。",
        "targets": ["/outside"],
        "implementationSize": "small",
    },
]


# ─── Ollama生成 ──────────────────────────────────────────────────────────────

def _build_prompt(planner_input: dict[str, Any]) -> str:
    rooms = planner_input.get("rooms", [])
    recent_accepted = planner_input.get("recentAccepted", [])
    recent_rejected = planner_input.get("recentRejected", [])

    room_summary = ", ".join(
        f"{r.get('name', '?')}({r.get('score', '?')})"
        for r in rooms[:6]
    ) if rooms else "データなし"

    accepted_titles = [p.get("title", "") for p in recent_accepted[:3]]
    rejected_titles = [p.get("title", "") for p in recent_rejected[:3]]

    return (
        "KYOUKAIは自己増殖する狂ったウェブサイトです。制作者向けの企画案を3件、日本語JSONで生成してください。\n\n"
        f"現在の部屋状態: {room_summary}\n"
        f"最近採用した企画: {', '.join(accepted_titles) if accepted_titles else 'なし'}\n"
        f"最近却下した企画: {', '.join(rejected_titles) if rejected_titles else 'なし'}\n\n"
        "企画案の形式（3件のJSON配列のみ。説明不要）:\n"
        '[{"title":"20字以内のタイトル","summary":"企画の概要（50字以内）",'
        '"reason":"なぜこの企画をするのか（30字以内）",'
        '"targets":["/対象ページ"],"implementationSize":"small"}]'
    )


def _extract_plans(text: str) -> list[dict[str, Any]] | None:
    match = re.search(r'\[.*?\]', text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group())
        if not isinstance(data, list):
            return None
        valid = [
            item for item in data
            if isinstance(item, dict) and "title" in item and "summary" in item
        ]
        return valid if valid else None
    except json.JSONDecodeError:
        return None


def _ollama_generate(planner_input: dict[str, Any]) -> list[dict[str, Any]] | None:
    prompt = _build_prompt(planner_input)
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.85, "num_predict": 400},
    }).encode("utf-8")
    try:
        req = UrlRequest(
            OLLAMA_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urlopen(req, timeout=10.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        raw = str(data.get("response", "")).strip()
        return _extract_plans(raw)
    except (OSError, URLError, TimeoutError, json.JSONDecodeError):
        pass
    return None


# ─── 公開API ─────────────────────────────────────────────────────────────────

def generate_plans(planner_input: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Generate AI plan proposals.

    Returns list of plan dicts with: id, title, summary, reason, targets,
    implementationSize, status, createdAt.
    Falls back to minimal placeholder plans if Ollama is unavailable.
    """
    now = datetime.now(timezone.utc).isoformat()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    raw_plans = _ollama_generate(planner_input)
    source = "ollama" if raw_plans else "fallback"
    if not raw_plans:
        raw_plans = list(_FALLBACK_PLANS)

    result = []
    for i, plan in enumerate(raw_plans[:5]):
        targets = plan.get("targets", ["/null"])
        if not isinstance(targets, list) or not targets:
            targets = ["/null"]

        result.append({
            "id": f"plan-{stamp}-{i + 1:02d}",
            "title": str(plan.get("title", "企画案"))[:40],
            "summary": str(plan.get("summary", ""))[:120],
            "reason": str(plan.get("reason", ""))[:80],
            "targets": targets,
            "implementationSize": str(plan.get("implementationSize", "small")),
            "status": "pending",
            "createdAt": now,
            "source": source,
        })

    return result
