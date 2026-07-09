#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 評議録(hyougi)

工程1時点では legacy_templates.py の関数をそのまま呼ぶ薄いラッパー。
見た目は旧デザインから1pxも変えない(リグレッション防止の移行措置)。
専用実装への置き換えは以降の工程(デザイン指針表を参照)で行う。
"""
import sys as _sys
from pathlib import Path as _Path
_BOOTH_DIR = _Path(__file__).resolve().parent.parent
if str(_BOOTH_DIR) not in _sys.path:
    _sys.path.insert(0, str(_BOOTH_DIR))
import legacy_templates as lt

_ROOM = {'id': 'hyougi', 'name': '評議録', 'color': '#ccbb99', 'rgb': '204,187,153', 'bg': '#080600', 'style': 'typewriter', 'label': '記録 進行中', 'source_label': '発言者', 'source': '不明', 'freq_label': '議事番号', 'fragments': ['誰かが発言した', '議題 曖昧', '結論 未達', '── いや', 'それは違う', '合意 不成立', '記録のみ残る', '発言者 不明', '── おそらく', '再度 確認'], 'brb_msgs': ['議事を一時中断しています', '記録を整理中', '次の発言を待機中', '発言者を確認中', '議題を再設定中'], 'brb_main': '議事を再開します', 'brb_bottom': '記録は継続されています', 'lt_label': '評議録'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "hyougi",
    "name": "評議録",
    "color": "#ccbb99",
    "rgb": "204,187,153",
    "bg": "#080600",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "記録は継続されています",
        "label": "記録 進行中",
        "brb_main": "議事を再開します",
    },
}
