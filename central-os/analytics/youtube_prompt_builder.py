"""
KYOUKAI Central OS — YouTube ショート企画プロンプトビルダー

使い方:
  python central-os/analytics/youtube_prompt_builder.py

youtube_analyzer.py 実行後に使う。
youtube_summary.json からショート案10本を提案するプロンプトを生成し、
Central OS の AI企画官に渡す入力を作る。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request as UrlRequest, urlopen

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ANALYTICS_DIR = BASE_DIR / "central-os" / "analytics"
LORE_FILE = BASE_DIR / "central-os" / "lore" / "kyoukai-world.md"
SUMMARY_JSON = ANALYTICS_DIR / "youtube_summary.json"
NEXT_SHORTS_JSON = ANALYTICS_DIR / "youtube_next_shorts.json"

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS = [
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "moonshotai/kimi-k2.6:free",
]


def _load_summary() -> dict:
    if not SUMMARY_JSON.exists():
        raise FileNotFoundError(f"{SUMMARY_JSON} が見つかりません。先に youtube_analyzer.py を実行してください。")
    return json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))


def _load_lore() -> str:
    if LORE_FILE.exists():
        return LORE_FILE.read_text(encoding="utf-8")
    return ""


def build_prompt(summary: dict) -> str:
    top = summary.get("topVideos", [])
    bottom = summary.get("bottomVideos", [])
    strong_words = summary.get("strongTitleWords", [])
    weak_words = summary.get("weakTitleWords", [])
    total = summary.get("videoCount", 0)
    days = summary.get("dayRange", 30)
    lore = _load_lore()

    top_lines = "\n".join(
        f"  - 「{v['title']}」 スコア:{v['score']} 再生:{v['views']} 維持率:{v['averageViewPercentage']}% 登録:{v['subscribersGained']}"
        for v in top[:5]
    ) or "  (データなし)"

    bottom_lines = "\n".join(
        f"  - 「{v['title']}」 スコア:{v['score']} 再生:{v['views']}"
        for v in bottom[:5]
    ) or "  (データなし)"

    lore_section = f"\n## KYOUKAIの世界観（必読）\n{lore}\n" if lore else ""

    return f"""あなたはKYOUKAIというアート・実験Webサイトの映像企画者です。
KYOUKAIのYouTube Shorts用の動画案を10本提案してください。
{lore_section}
## 分析データ（直近{days}日 / {total}本）

### 伸びた動画（上位）
{top_lines}

### 死んだ動画（下位）
{bottom_lines}

### 強いタイトルのキーワード
{', '.join(strong_words) if strong_words else 'なし'}

### 弱いタイトルのキーワード
{', '.join(weak_words) if weak_words else 'なし'}

## 制約
- KYOUKAIの世界観に忠実にすること
- ハウツー・解説・顔出し・明るいトーンは禁止
- タイトルは「〇〇とは？」「〇〇のやり方」型禁止
- 動画はアート・実験映像として提案する

## 出力形式（JSONのみ・説明不要）
[
  {{"title":"タイトル案（30字以内）","concept":"動画の核心（30字以内）","hook":"冒頭1秒のフック（20字以内）","reason":"なぜ伸びると思うか（30字以内）"}},
  ...
]

10本提案してください。"""


def _call_groq(prompt: str) -> str | None:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return None
    payload = json.dumps({
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85,
        "max_tokens": 1200,
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
        with urlopen(req, timeout=20.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return str(data["choices"][0]["message"]["content"]).strip()
    except Exception as e:
        print(f"[WARN] Groq: {e}")
    return None


def _call_openrouter(prompt: str) -> str | None:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return None
    for model in OPENROUTER_MODELS:
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.85,
            "max_tokens": 1200,
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
            with urlopen(req, timeout=25.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            text = str(data["choices"][0]["message"]["content"]).strip()
            if text:
                return text
        except Exception as e:
            print(f"[WARN] OpenRouter {model}: {e}")
    return None


def _extract_json_array(text: str) -> list | None:
    start = text.find("[")
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                try:
                    data = json.loads(text[start:i + 1])
                    if isinstance(data, list):
                        return data
                except json.JSONDecodeError:
                    return None
    return None


def generate_next_shorts() -> list[dict]:
    summary = _load_summary()
    prompt = build_prompt(summary)

    print("[INFO] ショート案を生成中 (Groq → OpenRouter → fallback)...")
    raw = _call_groq(prompt) or _call_openrouter(prompt)

    suggestions: list[dict] = []
    if raw:
        extracted = _extract_json_array(raw)
        if extracted:
            for item in extracted[:10]:
                if isinstance(item, dict) and "title" in item:
                    suggestions.append({
                        "title": str(item.get("title", ""))[:50],
                        "concept": str(item.get("concept", ""))[:80],
                        "hook": str(item.get("hook", ""))[:60],
                        "reason": str(item.get("reason", ""))[:80],
                    })

    source = "ai" if suggestions else "fallback"
    if not suggestions:
        print("[WARN] AI生成失敗。フォールバックなし（データ不足）。")
        suggestions = [{"title": "（AI生成失敗）", "concept": "APIキーを確認してください", "hook": "", "reason": ""}]

    from datetime import datetime, timezone
    output = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "basedOn": {
            "fetchedAt": summary.get("fetchedAt"),
            "analyzedAt": summary.get("analyzedAt"),
            "videoCount": summary.get("videoCount"),
        },
        "suggestions": suggestions,
    }

    try:
        NEXT_SHORTS_JSON.write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[OK] {NEXT_SHORTS_JSON}")
    except OSError as e:
        print(f"[WARN] ファイル書き込みスキップ: {e}")
    for i, s in enumerate(suggestions, 1):
        print(f"  {i:02d}. {s['title']} / {s['concept']}")
    return suggestions


if __name__ == "__main__":
    generate_next_shorts()
