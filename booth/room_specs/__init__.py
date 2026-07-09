#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_specs パッケージ

16部屋分の room_spec モジュールをまとめて読み込む load_all_specs() を提供する。
ファイル名にハイフンは使えないため、typhoon-news は typhoon_news.py に格納し、
SPEC内の "id" は 'typhoon-news' を維持する(ROADMAP記載の落とし穴対応)。
"""
import importlib
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_BOOTH_DIR = _THIS_DIR.parent
if str(_BOOTH_DIR) not in sys.path:
    sys.path.insert(0, str(_BOOTH_DIR))

# 部屋ID順(ROOMS定義の並び = legacy_templates.ROOMS の順)にモジュール名を列挙する。
# id -> モジュール名 (ハイフンはアンダースコアに置換)
ROOM_MODULE_NAMES = [
    "observation",
    "hyougi",
    "null",
    "observer",
    "exit",
    "archive",
    "ma",
    "daimyojin",
    "gokuraku",
    "particles",
    "ripple",
    "kanrinin",
    "namahage",
    "matsuri",
    "fukashitsu",
    "typhoon_news",
]


def load_all_specs():
    """16部屋のSPECを部屋ID順(ROOMS定義順)にimportしてリストで返す。"""
    specs = []
    for mod_name in ROOM_MODULE_NAMES:
        module = importlib.import_module(f"room_specs.{mod_name}")
        specs.append(module.SPEC)
    return specs
