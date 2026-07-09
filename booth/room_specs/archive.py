#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_spec: 記録室(archive)

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

_ROOM = {'id': 'archive', 'name': '記録室', 'color': '#8899aa', 'rgb': '136,153,170', 'bg': '#020408', 'style': 'files', 'label': '記録 照合中', 'source_label': '記録元', 'source': 'システム', 'freq_label': 'ファイルID', 'fragments': ['// file_001.log', '// file_002.log', '削除済み', '感情 排除', '記録 0x00441', '日付 不明', '// [REDACTED]', '存在 確認済み', '記録のみ残る', '感情なし'], 'brb_msgs': ['記録を参照しています', 'ファイルを整理中', '削除済みデータを確認中', 'アーカイブを検索中', '該当なし'], 'brb_main': '記録を参照しています', 'brb_bottom': '削除されたはずの記録が残っています', 'lt_label': '記録室'}


def waiting_html(spec):
    return lt.waiting_html(_ROOM)


def brb_html(spec):
    return lt.brb_html(_ROOM)


def lower_third_html(spec):
    return lt.lower_third_html(_ROOM)


SPEC = {
    "id": "archive",
    "name": "記録室",
    "color": "#8899aa",
    "rgb": "136,153,170",
    "bg": "#020408",
    "waiting_html": waiting_html,
    "brb_html": brb_html,
    "lower_third_html": lower_third_html,
    "readme_lines": {
        "brb_bottom": "削除されたはずの記録が残っています",
        "label": "記録 照合中",
        "brb_main": "記録を参照しています",
    },
}
