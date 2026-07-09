#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 極楽域(gokuraku)

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

_ROOM = {'id': 'gokuraku', 'name': '極楽域', 'color': '#ffaa44', 'rgb': '255,170,68', 'bg': '#040200', 'style': 'bars', 'label': '音源 再生中', 'source_label': '音源', 'source': '不明', 'freq_label': '音源番号', 'fragments': ['引き出し 1', '── 開かない', '音響装置 起動', '記憶の収納', '奥へ続く', '扉 発見', '鍵 必要', '音が聞こえる', '── 何の音か', '極楽 ではない'], 'brb_msgs': ['音源を調整しています', '引き出しを整理中', '奥への経路を確認中', '音響装置を再起動中', '記憶を参照しています'], 'brb_main': '音源を調整しています', 'brb_bottom': '奥への扉はまだ開いていません', 'lt_label': '極楽域'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "gokuraku",
    "name": "極楽域",
    "color": "#ffaa44",
    "rgb": "255,170,68",
    "bg": "#040200",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "奥への扉はまだ開いていません",
        "label": "音源 再生中",
        "brb_main": "音源を調整しています",
    },
}
