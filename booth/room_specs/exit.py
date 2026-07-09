#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 境界域(exit)

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

_ROOM = {'id': 'exit', 'name': '境界域', 'color': '#aaaaaa', 'rgb': '170,170,170', 'bg': '#050505', 'style': 'loader', 'label': '接続中', 'source_label': '接続先', 'source': '不明', 'freq_label': '経路番号', 'fragments': ['境界を越えようとしています', '接続中 ── ──', '少女の記録', '出口 不明', '越えた先', '接続 断絶', '戻れない', 'ロード中', '経路 消失', '境界'], 'brb_msgs': ['境界を超えようとしています', '接続経路を再構築中', '出口を探しています', '少女の記録を参照中', '経路が見つかりません'], 'brb_main': '境界を越えています', 'brb_bottom': '出口はまだ見つかっていません', 'lt_label': '境界域'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "exit",
    "name": "境界域",
    "color": "#aaaaaa",
    "rgb": "170,170,170",
    "bg": "#050505",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "出口はまだ見つかっていません",
        "label": "接続中",
        "brb_main": "境界を越えています",
    },
}
