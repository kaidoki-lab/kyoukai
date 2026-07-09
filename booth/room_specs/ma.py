#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 悪魔の間(ma)

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

_ROOM = {'id': 'ma', 'name': '悪魔の間', 'color': '#cc1122', 'rgb': '204,17,34', 'bg': '#040000', 'style': 'breathe', 'label': '存在 確認', 'source_label': '存在', 'source': '大魔将', 'freq_label': '訪問回数', 'fragments': ['また来たか', '── 黙れ', 'なぜここへ', '帰れ', '── いや', '少し', '待て', '何を求める', '大魔将は', '見ている'], 'brb_msgs': ['大魔将は沈黙しています', '存在は感知されています', '返答を待っています', '次の訪問を待っています', '── 黙って待て'], 'brb_main': '大魔将は沈黙しています', 'brb_bottom': '存在はここにある', 'lt_label': '悪魔の間'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "ma",
    "name": "悪魔の間",
    "color": "#cc1122",
    "rgb": "204,17,34",
    "bg": "#040000",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "存在はここにある",
        "label": "存在 確認",
        "brb_main": "大魔将は沈黙しています",
    },
}
