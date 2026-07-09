#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 粒子観測(particles)

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

_ROOM = {'id': 'particles', 'name': '粒子観測', 'color': '#4499ff', 'rgb': '68,153,255', 'bg': '#000408', 'style': 'particles', 'label': '粒子 観測中', 'source_label': '粒子源', 'source': '不明', 'freq_label': '粒子密度', 'fragments': ['粒子 検出', '運動 継続中', '意味 後から', '軌跡 記録', '衝突 回避', '密度 変化', '方向 不定', '観測 先行', '── 意味は', '粒子の群れ'], 'brb_msgs': ['粒子を追跡中です', '軌跡を記録しています', '新しい粒子を検出中', '観測データを処理中', '粒子が集まっています'], 'brb_main': '粒子を観測しています', 'brb_bottom': '運動は意味の前にある', 'lt_label': '粒子観測'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "particles",
    "name": "粒子観測",
    "color": "#4499ff",
    "rgb": "68,153,255",
    "bg": "#000408",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "運動は意味の前にある",
        "label": "粒子 観測中",
        "brb_main": "粒子を観測しています",
    },
}
