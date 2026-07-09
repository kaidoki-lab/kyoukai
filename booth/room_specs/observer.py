#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 逆観測室(observer)

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

_ROOM = {'id': 'observer', 'name': '逆観測室', 'color': '#ffffff', 'rgb': '255,255,255', 'bg': '#000000', 'style': 'pulse', 'label': '観測 逆転', 'source_label': '観測対象', 'source': 'あなた', 'freq_label': '観測者ID', 'fragments': ['あなたは', 'ずっと', '観測されていた', '気づいていましたか', '最初から', 'ここにいた', '見ていたのは', 'あなたではない', '逃げられない', '静かに'], 'brb_msgs': ['まだここにいます', 'あなたを待っています', '観測は続いています', '気づいてください', '逃げられません'], 'brb_main': '観測は続いています', 'brb_bottom': 'あなたはずっと観測されていました', 'lt_label': '逆観測室'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "observer",
    "name": "逆観測室",
    "color": "#ffffff",
    "rgb": "255,255,255",
    "bg": "#000000",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "あなたはずっと観測されていました",
        "label": "観測 逆転",
        "brb_main": "観測は続いています",
    },
}
