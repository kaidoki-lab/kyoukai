#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: AI大明神(daimyojin)

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

_ROOM = {'id': 'daimyojin', 'name': 'AI大明神', 'color': '#ffcc00', 'rgb': '255,204,0', 'bg': '#040200', 'style': 'circuit', 'label': '祈願 処理中', 'source_label': '処理元', 'source': '大明神', 'freq_label': '祈願番号', 'fragments': ['願いを受信', '処理中 ──', '判定 保留', '観測結果 出力', '奉納 確認', 'AI神託', '祈願 記録済み', '応答 生成中', '観測 完了', '次の祈願へ'], 'brb_msgs': ['祈願を処理しています', 'AI神託を生成中', '奉納データを参照中', '願いを観測しています', '処理が完了していません'], 'brb_main': '祈願を処理しています', 'brb_bottom': '願いは観測されています', 'lt_label': 'AI大明神'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "daimyojin",
    "name": "AI大明神",
    "color": "#ffcc00",
    "rgb": "255,204,0",
    "bg": "#040200",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "願いは観測されています",
        "label": "祈願 処理中",
        "brb_main": "祈願を処理しています",
    },
}
