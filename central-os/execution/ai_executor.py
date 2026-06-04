"""
KYOUKAI Central OS — AI実装監督 v1
採用済み企画案を受け取り、Codex用の作業指示書を生成する。

Ollama接続時  : ローカルAIが実装指示書を生成
Ollama未接続時: フォールバック（骨組みのみ）を返す
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

# ─── 共通ルール ──────────────────────────────────────────────────────────────

_MUST_KEEP = [
    "KYOUKAIをゲーム化しない",
    "実績解除や進行状況をユーザーに表示しない",
    "ユーザーにCentral OSの存在を見せない",
    "ホラーではなく、狂った日本的な異常サイトとして扱う",
    "Central OSは制作者専用であり、ユーザー向けに露出しない",
]

_DO_NOT_CHANGE = [
    "GA4接続処理",
    "AI分析官 (central-os/analysis/ai_analyst.py)",
    "AI企画官 (central-os/planning/ai_planner.py)",
    "既存の採用/保留/却下API",
    "秘密情報やcredentials関連",
    "gitignore設定",
]

_COMMON_CRITERIA = [
    "対象ページが正常表示される",
    "既存ページが壊れていない",
    "Central OSやゲーム的UIがユーザー向けに露出していない",
    "git statusに秘密情報が含まれていない",
]

_COMMON_STEPS = [
    "現行ルートとテンプレート構造を確認する",
    "対象ページに必要な最小変更を加える",
    "既存導線を壊さないか確認する",
    "ローカル表示を確認する",
]


# ─── フォールバック ──────────────────────────────────────────────────────────

def _fallback_task_body(plan: dict[str, Any]) -> dict[str, Any]:
    targets = plan.get("targets", ["/null"])
    candidate_files = ["main.py"]
    for t in targets[:3]:
        slug = t.strip("/").replace("/", "_") or "index"
        candidate_files.append(f"templates/{slug}.html")
    candidate_files.append("（現行構造を確認してから判断）")

    return {
        "objective": plan.get("summary", "")[:100],
        "implementationBrief": (
            f"{plan.get('summary', '')} "
            "詳細な実装方法は現行構造を確認してから判断すること。"
        )[:200],
        "candidateFiles": candidate_files,
        "steps": list(_COMMON_STEPS),
        "acceptanceCriteria": list(_COMMON_CRITERIA),
    }


# ─── Ollama生成 ──────────────────────────────────────────────────────────────

def _build_prompt(plan: dict[str, Any], context: dict[str, Any]) -> str:
    targets = ", ".join(plan.get("targets", ["/null"]))
    project_rule = context.get(
        "projectRule",
        "KYOUKAIは自己増殖する狂ったウェブサイトです。ゲームではない。",
    )
    return (
        "KYOUKAIウェブサイトの実装作業指示書を日本語JSONで生成してください。\n\n"
        f"企画タイトル: {plan.get('title', '')}\n"
        f"企画概要: {plan.get('summary', '')}\n"
        f"理由: {plan.get('reason', '')}\n"
        f"対象ページ: {targets}\n"
        f"プロジェクト方針: {project_rule}\n\n"
        "回答形式（JSONのみ。説明不要）:\n"
        '{"objective":"実装目的（50字以内）",'
        '"implementationBrief":"具体的な実装概要（100字以内）",'
        '"candidateFiles":["ファイル名1","ファイル名2"],'
        '"steps":["手順1","手順2","手順3"],'
        '"acceptanceCriteria":["条件1","条件2","条件3"]}'
    )


def _extract_task_body(text: str) -> dict[str, Any] | None:
    match = re.search(r'\{[^{}]*"objective"[^{}]*\}', text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group())
        if "objective" in data and "implementationBrief" in data:
            return data
    except json.JSONDecodeError:
        pass
    return None


def _ollama_generate(plan: dict[str, Any], context: dict[str, Any]) -> dict[str, Any] | None:
    prompt = _build_prompt(plan, context)
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.75, "num_predict": 350},
    }).encode("utf-8")
    try:
        req = UrlRequest(
            OLLAMA_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urlopen(req, timeout=10.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        raw = str(data.get("response", "")).strip()
        return _extract_task_body(raw)
    except (OSError, URLError, TimeoutError, json.JSONDecodeError):
        pass
    return None


# ─── 公開API ─────────────────────────────────────────────────────────────────

_KYOUKAI_CONTEXT: dict[str, Any] = {
    "projectRule": "KYOUKAIはゲームではなく、自己増殖し続ける狂ったウェブサイトである。",
    "doNotGamify": True,
    "centralOsRole": "Central OSは制作者専用の私用増殖管理OSであり、ユーザーには見せない。",
}


def generate_task(plan: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Generate a Codex-ready implementation task from an approved plan.

    Returns a task dict with all required fields.
    Falls back to minimal skeleton if Ollama is unavailable.
    """
    ctx = dict(_KYOUKAI_CONTEXT)
    if context:
        ctx.update(context)

    now = datetime.now(timezone.utc).isoformat()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    plan_id = plan.get("id", "unknown")

    ai_body = _ollama_generate(plan, ctx)
    source = "ollama" if ai_body else "fallback"
    if not ai_body:
        ai_body = _fallback_task_body(plan)

    # normalize list fields
    def _to_list(val: Any, default: list) -> list:
        if isinstance(val, list):
            return [str(v) for v in val if v]
        return list(default)

    return {
        "id": f"task-{stamp}",
        "sourcePlanId": plan_id,
        "createdAt": now,
        "title": f"{plan.get('title', '企画')} 実装指示",
        "targetPages": list(plan.get("targets", ["/null"])),
        "objective": str(ai_body.get("objective", ""))[:120],
        "implementationBrief": str(ai_body.get("implementationBrief", ""))[:300],
        "candidateFiles": _to_list(ai_body.get("candidateFiles"), ["main.py"]),
        "mustKeep": list(_MUST_KEEP),
        "doNotChange": list(_DO_NOT_CHANGE),
        "steps": _to_list(ai_body.get("steps"), _COMMON_STEPS),
        "acceptanceCriteria": _to_list(ai_body.get("acceptanceCriteria"), _COMMON_CRITERIA),
        "status": "pending",
        "codexReady": False,
        "source": source,
    }
