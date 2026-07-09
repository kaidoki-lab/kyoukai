#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 台風ニュース(typhoon-news)

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

_ROOM = {'id': 'typhoon-news', 'name': '台風ニュース', 'color': '#ff0033', 'rgb': '255,0,51', 'bg': '#000010', 'style': 'ticker', 'label': '速報 送信中', 'source_label': '情報源', 'source': '気象庁', 'freq_label': '台風番号', 'fragments': ['台風接近中', '── 後ほど連絡します', '速報 発令', '検討します', 'お母さんに聞いて', '警戒レベル上昇', '── 了解しました', '避難勧告 発令', 'ただいま調整中', '続報をお待ちください'], 'brb_msgs': ['速報を準備しています', '台風情報を更新中', '気象データを処理中', '続報をお待ちください', '情報を確認中です'], 'brb_main': '速報を準備しています', 'brb_bottom': '続報をお待ちください', 'lt_label': '台風ニュース'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "typhoon-news",
    "name": "台風ニュース",
    "color": "#ff0033",
    "rgb": "255,0,51",
    "bg": "#000010",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "続報をお待ちください",
        "label": "速報 送信中",
        "brb_main": "速報を準備しています",
    },
}
