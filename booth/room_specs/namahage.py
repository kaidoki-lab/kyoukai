#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: なまはげ(namahage)

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

_ROOM = {'id': 'namahage', 'name': 'なまはげ', 'color': '#ff2200', 'rgb': '255,34,0', 'bg': '#040000', 'style': 'eye', 'label': '観測 中', 'source_label': '存在', 'source': 'なまはげ', 'freq_label': '訪問番号', 'fragments': ['泣く子はいねぇか', '── いる', '目が光った', '長押しするな', '── するな', '見ている', 'タップ 検出', '── やめろ', 'なまはげ 起動', '逃げられない'], 'brb_msgs': ['なまはげを呼んでいます', '目が光っています', '存在を確認中', '泣く子を探しています', '── いるか'], 'brb_main': 'なまはげを呼んでいます', 'brb_bottom': '泣く子はいねぇか', 'lt_label': 'なまはげ'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "namahage",
    "name": "なまはげ",
    "color": "#ff2200",
    "rgb": "255,34,0",
    "bg": "#040000",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "泣く子はいねぇか",
        "label": "観測 中",
        "brb_main": "なまはげを呼んでいます",
    },
}
