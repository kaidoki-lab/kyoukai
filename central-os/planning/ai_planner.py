"""
KYOUKAI Central OS — AI企画官 v1
GA4分析・観測データを受け取り、自由な企画案を生成する。

優先順位:
  1. Ollama（ローカル起動中の場合）
  2. Groq API（GROQ_API_KEY 環境変数がある場合）
  3. フォールバック（固定テンプレート）
"""

from __future__ import annotations

import json
import os
import random
import re
from datetime import datetime, timezone
from typing import Any
from urllib.error import URLError
from urllib.request import Request as UrlRequest, urlopen

OLLAMA_URL          = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL        = "qwen2.5:0.5b"
GROQ_API_URL        = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL          = "llama-3.1-8b-instant"
OPENROUTER_API_URL  = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS   = [
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "moonshotai/kimi-k2.6:free",
]

# ─── フォールバック仮企画プール（ランダム選択・重複回避用） ──────────────────

_FALLBACK_POOL = [
    {
        "title": "崩落域の記憶断片追加",
        "summary": "/nullに断片化したテキストを追加し、「なにかがあった」という印象を与える。",
        "reason": "崩落域への反応があり、さらなる深みで滞在時間が伸びる可能性がある。",
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
        "reason": "外部接続を「狂った境界」として演出し世界観を強化する。",
        "targets": ["/outside"],
        "implementationSize": "small",
    },
    {
        "title": "archive残留ログの追加",
        "summary": "/archiveに新しい断片ログを1件追加し、記録室の密度を上げる。",
        "reason": "記録室への関心が確認されており、コンテンツ追加で深みが増す。",
        "targets": ["/archive"],
        "implementationSize": "small",
    },
    {
        "title": "受信域の信号断片更新",
        "summary": "/signalのラジオテキストを1件更新し、受信体験を新鮮に保つ。",
        "reason": "受信域は滞在時間が長く、テキスト更新で再訪問を促せる。",
        "targets": ["/signal"],
        "implementationSize": "small",
    },
    {
        "title": "祭壇域の導線テキスト変更",
        "summary": "トップページの/observationへの誘導テキストを微調整する。",
        "reason": "入口の言葉が全体の滞在率を左右するため。",
        "targets": ["/"],
        "implementationSize": "small",
    },
    {
        "title": "逆観測室への隠れたリンク",
        "summary": "/observerへの導線を深い場所に1箇所追加する。",
        "reason": "逆観測室はまだ発見されにくいため、深層導線を強化する。",
        "targets": ["/observer"],
        "implementationSize": "small",
    },
    {
        "title": "崩壊域の遷移演出強化",
        "summary": "/exitの遷移テキストを1件追加し、境界体験を深める。",
        "reason": "境界域への反応があり、遷移演出が世界観の核になっている。",
        "targets": ["/exit"],
        "implementationSize": "small",
    },
    {
        "title": "null接続後のarchive誘導",
        "summary": "/nullから/archiveへの残留リンクをひっそりと追加する。",
        "reason": "崩落を体験した訪問者が記録室へ流れる導線を作る。",
        "targets": ["/null", "/archive"],
        "implementationSize": "small",
    },
    {
        "title": "観測ログの新規追加",
        "summary": "/observationの生命体ログを1件追加し、観測体験を更新する。",
        "reason": "観測域は最も反応が強く、更新頻度が再訪問率に直結する。",
        "targets": ["/observation"],
        "implementationSize": "small",
    },
    {
        "title": "外部アイコンの種類追加",
        "summary": "/outsideに新しいアイコンパターンを1種追加する。",
        "reason": "外部接続の探索行動が確認されており、発見要素を増やす。",
        "targets": ["/outside"],
        "implementationSize": "small",
    },
    {
        "title": "hyougi録の断片テキスト追加",
        "summary": "/hyougiに評議断片テキストを1件追加する。",
        "reason": "評議録への流入はあるが内容が薄く、密度を上げる必要がある。",
        "targets": ["/hyougi"],
        "implementationSize": "small",
    },
]


def _pick_fallback(excluded_titles: set[str], count: int = 3) -> list[dict]:
    """採用済みタイトルを除いてランダムに企画を選ぶ。"""
    available = [p for p in _FALLBACK_POOL if p["title"] not in excluded_titles]
    if not available:
        available = list(_FALLBACK_POOL)  # 全部除外されたら全部から選ぶ
    return random.sample(available, min(count, len(available)))


# ─── プロンプト ──────────────────────────────────────────────────────────────

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
    """入れ子構造に対応したJSON配列抽出。"""
    start = text.find('[')
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                try:
                    data = json.loads(text[start:i + 1])
                    if not isinstance(data, list):
                        return None
                    valid = [
                        item for item in data
                        if isinstance(item, dict) and "title" in item and "summary" in item
                    ]
                    return valid if valid else None
                except json.JSONDecodeError:
                    return None
    return None


# ─── Ollama ──────────────────────────────────────────────────────────────────

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


# ─── Groq API ────────────────────────────────────────────────────────────────

def _groq_generate(planner_input: dict[str, Any]) -> list[dict[str, Any]] | None:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return None
    prompt = _build_prompt(planner_input)
    payload = json.dumps({
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85,
        "max_tokens": 600,
    }).encode("utf-8")
    try:
        req = UrlRequest(
            GROQ_API_URL, data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "Mozilla/5.0 (compatible; KYOUKAI-OS/1.0)",
            },
            method="POST",
        )
        with urlopen(req, timeout=15.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        raw = str(data["choices"][0]["message"]["content"]).strip()
        return _extract_plans(raw)
    except (OSError, URLError, TimeoutError, json.JSONDecodeError, KeyError):
        pass
    return None


# ─── OpenRouter API ──────────────────────────────────────────────────────────

def _openrouter_generate(planner_input: dict[str, Any]) -> list[dict[str, Any]] | None:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return None
    prompt = _build_prompt(planner_input)
    for model in OPENROUTER_MODELS:
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.85,
            "max_tokens": 600,
        }).encode("utf-8")
        try:
            req = UrlRequest(
                OPENROUTER_API_URL, data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://www.void-kyoukai.net",
                },
                method="POST",
            )
            with urlopen(req, timeout=20.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            raw = str(data["choices"][0]["message"]["content"]).strip()
            result = _extract_plans(raw)
            if result:
                return result
        except (OSError, URLError, TimeoutError, json.JSONDecodeError, KeyError):
            pass
    return None


# ─── 公開API ─────────────────────────────────────────────────────────────────

def generate_plans(planner_input: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Generate AI plan proposals.

    Priority: Ollama → Groq API → fallback
    """
    now = datetime.now(timezone.utc).isoformat()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    # 採用済み企画のタイトルセットを作る（重複除外用）
    accepted = planner_input.get("recentAccepted", [])
    excluded_titles: set[str] = {p.get("title", "") for p in accepted if p.get("title")}

    raw_plans = _ollama_generate(planner_input)
    source = "ollama"

    if not raw_plans:
        raw_plans = _groq_generate(planner_input)
        source = "groq"

    if not raw_plans:
        raw_plans = _openrouter_generate(planner_input)
        source = "openrouter"

    if not raw_plans:
        raw_plans = _pick_fallback(excluded_titles, count=3)
        source = "fallback"

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
