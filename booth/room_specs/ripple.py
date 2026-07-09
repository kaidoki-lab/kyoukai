#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 波紋域(ripple)

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

_ROOM = {'id': 'ripple', 'name': '波紋域', 'color': '#00ccbb', 'rgb': '0,204,187', 'bg': '#000604', 'style': 'ripple', 'label': '応答 検出', 'source_label': '応答源', 'source': '未知', 'freq_label': '波紋番号', 'fragments': ['触れると応答する', '一点だけ', '命令を聞かない', '波紋 観測中', '反応 検出', '異常ドット 確認', '── 逃げた', '世界が応答する', '触れるな', '── 触れろ'], 'brb_msgs': ['波紋を観測しています', '異常ドットを追跡中', '応答を待っています', '世界の反応を記録中', '一点だけ応答しません'], 'brb_main': '波紋を観測しています', 'brb_bottom': '触れると世界が応答します', 'lt_label': '波紋域'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "ripple",
    "name": "波紋域",
    "color": "#00ccbb",
    "rgb": "0,204,187",
    "bg": "#000604",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "触れると世界が応答します",
        "label": "応答 検出",
        "brb_main": "波紋を観測しています",
    },
}
