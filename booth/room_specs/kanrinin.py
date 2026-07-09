#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 管理人室(kanrinin)

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

_ROOM = {'id': 'kanrinin', 'name': '管理人室', 'color': '#aa8855', 'rgb': '170,136,85', 'bg': '#050300', 'style': 'retro', 'label': '管理 継続中', 'source_label': '室内状況', 'source': '管理人', 'freq_label': '入室番号', 'fragments': ['管理人 不在', '呼び鈴 未応答', '鍵 管理中', '消滅の鍵 保管', 'BOOTH 荷物あり', '日誌 更新済み', '── いらっしゃい', '賽銭箱 確認', '目玉 観測', '管理日誌 閲覧可'], 'brb_msgs': ['管理人を呼んでいます', '呼び鈴を鳴らしています', '管理人は席を外しています', '日誌を確認中です', 'しばらくお待ちください'], 'brb_main': '管理人は席を外しています', 'brb_bottom': 'しばらくお待ちください', 'lt_label': '管理人室'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "kanrinin",
    "name": "管理人室",
    "color": "#aa8855",
    "rgb": "170,136,85",
    "bg": "#050300",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "しばらくお待ちください",
        "label": "管理 継続中",
        "brb_main": "管理人は席を外しています",
    },
}
