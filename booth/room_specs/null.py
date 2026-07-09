#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 崩落域(null)

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

_ROOM = {'id': 'null', 'name': '崩落域', 'color': '#ff4433', 'rgb': '255,68,51', 'bg': '#080000', 'style': 'glitch', 'label': '崩壊 進行中', 'source_label': '崩壊源', 'source': '不明', 'freq_label': '崩壊度', 'fragments': ['接続 悪化', 'データ 欠損', '── 取得失敗', '崩壊度 上昇', 'ERROR', 'NULL', '── ──', '回復 不能', '押すな', '悪化している'], 'brb_msgs': ['崩落を記録中です', 'データを回収しています', '接続を維持しようとしています', '崩壊が続いています', '戻れません'], 'brb_main': '崩落は続いています', 'brb_bottom': '接続は不安定なまま維持されています', 'lt_label': '崩落域'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "null",
    "name": "崩落域",
    "color": "#ff4433",
    "rgb": "255,68,51",
    "bg": "#080000",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "接続は不安定なまま維持されています",
        "label": "崩壊 進行中",
        "brb_main": "崩落は続いています",
    },
}
