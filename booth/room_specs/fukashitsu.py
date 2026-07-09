#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 卵部屋(fukashitsu)

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

_ROOM = {'id': 'fukashitsu', 'name': '卵部屋', 'color': '#ffaacc', 'rgb': '255,170,204', 'bg': '#050003', 'style': 'glow', 'label': '孵化 観測中', 'source_label': '状態', 'source': '卵', 'freq_label': '温度', 'fragments': ['卵 観察中', '栄養 注入', '酸素 供給', '温度 維持', '── もうすぐ', 'パーティクル 変化', '色が変わった', '取り出せる', '── まだ', '孵化 待機中'], 'brb_msgs': ['卵を観察しています', '温度を維持中です', '栄養を補給しています', '孵化を待っています', '── もうすぐです'], 'brb_main': '卵を観察しています', 'brb_bottom': '孵化まで観測を継続します', 'lt_label': '卵部屋'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "fukashitsu",
    "name": "卵部屋",
    "color": "#ffaacc",
    "rgb": "255,170,204",
    "bg": "#050003",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "孵化まで観測を継続します",
        "label": "孵化 観測中",
        "brb_main": "卵を観察しています",
    },
}
