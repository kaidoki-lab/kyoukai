#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 観測域(observation)

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

_ROOM = {'id': 'observation', 'name': '観測域', 'color': '#44ff88', 'rgb': '68,255,136', 'bg': '#000800', 'style': 'log', 'label': '観測継続中', 'source_label': '観測対象', 'source': '不明', 'freq_label': '観測ID', 'fragments': ['観測記録 更新中', '生命体 確認', 'ログ 蓄積中', '感情 排除済み', '対象 識別中', '観測継続', '異常 なし', '// LOG_BUFFER_FULL', '記録中', '応答 検出'], 'brb_msgs': ['観測を一時停止しています', 'ログを保存中', '次の観測まで待機中', '対象を再捕捉中', '記録を圧縮中'], 'brb_main': '観測を再開します', 'brb_bottom': '対象の観測は継続されています', 'lt_label': '観測域'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "observation",
    "name": "観測域",
    "color": "#44ff88",
    "rgb": "68,255,136",
    "bg": "#000800",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "対象の観測は継続されています",
        "label": "観測継続中",
        "brb_main": "観測を再開します",
    },
}
