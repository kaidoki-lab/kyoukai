#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 棒入れ祭(matsuri)

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

_ROOM = {'id': 'matsuri', 'name': '棒入れ祭', 'color': '#ffdd00', 'rgb': '255,221,0', 'bg': '#040200', 'style': 'festival', 'label': '奉納 進行中', 'source_label': '状況', 'source': '参拝者', 'freq_label': '奉納回数', 'fragments': ['奉納を開始', 'ヨイショ ──', 'まだ足りない', '後退した', 'もう少し', '観衆の声', '紙吹雪 飛散', '── 頑張れ', '奉納完了 間近', 'ヨイショーー！'], 'brb_msgs': ['奉納の準備をしています', '観衆が集まっています', '棒を準備中です', '奉納を再開します', '── 急いで'], 'brb_main': '奉納の準備をしています', 'brb_bottom': '奉納は継続されています', 'lt_label': '棒入れ祭'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "matsuri",
    "name": "棒入れ祭",
    "color": "#ffdd00",
    "rgb": "255,221,0",
    "bg": "#040200",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "奉納は継続されています",
        "label": "奉納 進行中",
        "brb_main": "奉納の準備をしています",
    },
}
