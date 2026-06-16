"""
KYOUKAI Central OS — AI分析官 v1
GA4分析結果を受け取り、考察・仮説・推奨アクションを生成する。

Ollama接続時  : ローカルAIが考察を生成
Ollama未接続時: ルールベースのフォールバック考察を返す
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.error import URLError
from urllib.request import Request as UrlRequest, urlopen

OLLAMA_URL   = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:0.5b"

# ─── ルールベースフォールバック ─────────────────────────────────────────────

_RULE_TABLE: dict[str, dict[str, Any]] = {
    "/": {
        "analysis": "メイン入口のPVが最高。多くの観測者が祭壇域から体験を始めており、入口体験が全体の印象を決定づけている。",
        "hypothesis": "祭壇域の第一印象がKYOUKAI全体の滞在意欲を左右している。",
        "recommendations": ["祭壇域ビジュアルを更新する", "/observationへの導線を強化する", "null接続テキストを追加する"],
    },
    "/null": {
        "analysis": "崩落域への反応が高い。訪問者は意図的に崩落した接続を探している可能性がある。",
        "hypothesis": "不明瞭な接続そのものが体験の中核になっている。",
        "recommendations": ["崩落テキストを1件追加する", "null専用ログを生成する", "/archiveへ残留リンクを設置する"],
    },
    "/observation": {
        "analysis": "観測体験への関心が高い。滞在時間が長い場合は生命体との対話を求めている可能性がある。",
        "hypothesis": "能動的な観測行動が発生しており、インタラクション密度が重要である。",
        "recommendations": ["観測ログを1件追加する", "生命体変化の演出を強化する", "コマンド種類を拡充する"],
    },
    "/outside": {
        "analysis": "外部接続への興味が強い。outsideへの流入は意図的な探索の結果である可能性がある。",
        "hypothesis": "ユーザーは境界の外側を積極的に調べており、外部導線が機能している。",
        "recommendations": ["外部アイコンを1種類追加する", "自販機テキストを更新する", "接続信号テキストを更新する"],
    },
    "/exit": {
        "analysis": "境界域への反応が高い。訪問者は出口ではなく接続先への期待を持っている可能性がある。",
        "hypothesis": "遷移体験そのものへの興味が集中している。",
        "recommendations": ["少女ログを1件追加する", "ロード演出を強化する", "接続先の分岐テキストを追加する"],
    },
    "/archive": {
        "analysis": "記録室への関心がある。過去ログへの探索行動が発生している。",
        "hypothesis": "KYOUKAIの歴史・断片への興味がユーザーを引き寄せている。",
        "recommendations": ["archive-logを1件追加する", "記録断片テキストを生成する", "/nullへの残留リンクを追加する"],
    },
    "/signal": {
        "analysis": "受信域への反応がある。意味不明な信号テキストへの引力が機能している。",
        "hypothesis": "ノイズ的なテキストが体験の引力になっている。",
        "recommendations": ["受信断片テキストを1件追加する", "ラジオ放送テキストを更新する", "/outsideへの接続信号を追加する"],
    },
}

_DEFAULT_ANALYSIS: dict[str, Any] = {
    "analysis": "このページへの反応が確認された。変化候補として記録する。",
    "hypothesis": "導線または内容に反応が発生している。",
    "recommendations": ["ページの内容を見直す", "導線の配置を確認する", "関連ページへの接続を検討する"],
}


def _rule_based(page: str) -> dict[str, Any]:
    return dict(_RULE_TABLE.get(page, _DEFAULT_ANALYSIS))


# ─── Ollama生成 ─────────────────────────────────────────────────────────────

def _build_prompt(page: str, pv: int, dur: float, bounce: float, priority: str, event_note: str = "") -> str:
    event_section = f"\nイベント観測（本日）: {event_note}\n" if event_note else ""
    return (
        f"KYOUKAIは自己増殖するウェブサイトです。"
        f"以下のGA4データを日本語で分析し、JSONのみで回答してください。\n\n"
        f"ページ: {page}  PV(30日): {pv}  平均滞在: {round(dur,1)}秒  直帰率: {round(bounce*100,1)}%  優先度: {priority}\n"
        f"{event_section}\n"
        f"回答形式（JSONのみ。説明不要）:\n"
        f'{{\"analysis\":\"考察文（50字以内）\",\"hypothesis\":\"仮説（30字以内）\",'
        f'\"recommendations\":[\"推奨1\",\"推奨2\",\"推奨3\"]}}'
    )


def _extract_json(text: str) -> dict[str, Any] | None:
    """Extract first JSON object from Ollama response."""
    match = re.search(r'\{[^{}]*"analysis"[^{}]*\}', text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


def _ollama_analyze(page: str, pv: int, dur: float, bounce: float, priority: str, event_note: str = "") -> dict[str, Any] | None:
    prompt = _build_prompt(page, pv, dur, bounce, priority, event_note)
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 200},
    }).encode("utf-8")
    try:
        req = UrlRequest(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=6.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        raw = str(data.get("response", "")).strip()
        result = _extract_json(raw)
        if result and all(k in result for k in ("analysis", "hypothesis", "recommendations")):
            return result
    except (OSError, URLError, TimeoutError, json.JSONDecodeError):
        pass
    return None


# ─── 公開API ─────────────────────────────────────────────────────────────────

def analyze_page(
    page: str,
    pv: int = 0,
    avg_duration: float = 0.0,
    bounce_rate: float = 0.0,
    priority: str = "low",
    use_ollama: bool = True,
    event_note: str = "",
) -> dict[str, Any]:
    """
    Return AI analysis for a GA4 page entry.

    event_note: Central OSのイベント観測（room_enter_*, ofuse_click等）から
    作られた一言サマリー。GA4イベントが導線・離脱・外部接続の判断材料になる。

    Returns dict with keys: analysis, hypothesis, recommendations
    Falls back to rule-based if Ollama is unavailable or returns malformed JSON.
    """
    if use_ollama:
        result = _ollama_analyze(page, pv, avg_duration, bounce_rate, priority, event_note)
        if result:
            return result
    result = _rule_based(page)
    if event_note:
        result["analysis"] = (result.get("analysis", "") + f" [イベント観測: {event_note}]").strip()
    return result
