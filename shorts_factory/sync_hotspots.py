"""
KYOUKAI Shorts Factory — ホットスポット自動同期
kyoukai-world.md と templates/*.html を読んで
kyoukai_hotspots.json を自動更新する。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CENTRAL_OS = ROOT.parent / "central-os"
TEMPLATES = ROOT.parent / "templates"

LORE_PATH = CENTRAL_OS / "lore" / "kyoukai-world.md"
HOTSPOTS_PATH = ROOT / "kyoukai_hotspots.json"

# ページルート → テンプレートファイルのマッピング
ROUTE_TO_TEMPLATE = {
    "/":                "index.html",
    "/observation":     "observer.html",  # 観測域
    "/signal":          "signal.html",
    "/external-signal": "external-signal.html",
    "/null":            "null.html",
    "/observer":        "observer.html",  # 逆観測室
    "/exit":            "exit.html",
    "/archive":         "archive.html",
    "/outside":         "outside.html",
    "/ma":              "ma.html",
    "/hyougi":          "hyougi.html",
}

# 観測域は observation.html がない場合 observer.html を確認
ROUTE_TO_TEMPLATE_ALT = {
    "/observation": "observation.html",
}


def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_lore_from_md(md_text: str) -> dict[str, dict]:
    """kyoukai-world.md から各部屋のルート・名前・ロアを抽出する。"""
    rooms: dict[str, dict] = {}

    # テーブルから部屋名とルートを抽出
    # | 祭壇域 | / | KYOUKAIへの入口。...
    table_pattern = re.compile(r"\|\s*([^|]+?)\s*\|\s*(/[^\s|]*)\s*\|")
    for match in table_pattern.finditer(md_text):
        room_name = match.group(1).strip()
        route = match.group(2).strip()
        if route not in rooms:
            rooms[route] = {"room_name": room_name, "lore": "", "narrative_purpose": ""}

    # 各部屋の詳細セクションからロアを抽出
    # ### 祭壇域（/） から次の ### まで
    section_pattern = re.compile(
        r"###\s+(.+?)\n(.*?)(?=###|\Z)", re.DOTALL
    )
    for match in section_pattern.finditer(md_text):
        header = match.group(1).strip()
        body = match.group(2).strip()

        # ヘッダーからルートを抽出（全角・半角括弧どちらも対応）
        # 例: 祭壇域（/）or 祭壇域(/)
        route_match = re.search(r"[（(](/[^）)]*)[）)]", header)
        if not route_match:
            continue
        route = route_match.group(1).strip()

        # 部屋名（括弧より前）
        room_name = re.sub(r"[（(].*[）)]", "", header).strip()

        # ロア: 箇条書きを含む本文全体
        lore_lines = []
        for line in body.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                lore_lines.append(line.lstrip("- "))

        lore = " ".join(lore_lines[:5])  # 最初の5文まで

        if route not in rooms:
            rooms[route] = {"room_name": room_name, "lore": lore, "narrative_purpose": ""}
        else:
            rooms[route]["lore"] = lore
            if not rooms[route].get("room_name"):
                rooms[route]["room_name"] = room_name

    return rooms


def scan_interactions(template_path: Path) -> list[dict]:
    """HTMLファイルからインタラクティブ要素を抽出する。"""
    if not template_path.exists():
        return []

    html = template_path.read_text(encoding="utf-8")
    interactions = []

    # <button> タグ
    for match in re.finditer(
        r'<button([^>]*)>(.*?)</button>', html, re.DOTALL
    ):
        attrs = match.group(1)
        inner = re.sub(r"<[^>]+>", "", match.group(2)).strip()

        classes = re.search(r'class=["\']([^"\']+)["\']', attrs)
        id_attr = re.search(r'id=["\']([^"\']+)["\']', attrs)
        aria = re.search(r'aria-label=["\']([^"\']+)["\']', attrs)
        data = re.search(r'data-[\w-]+=["\']([^"\']+)["\']', attrs)

        selector = ""
        name = inner or (aria.group(1) if aria else "")
        if id_attr:
            selector = f"#{id_attr.group(1)}"
        elif classes:
            cls_list = classes.group(1).split()
            selector = "." + cls_list[0]
            if len(cls_list) > 1:
                selector += "." + cls_list[1]
            if data:
                data_key = re.search(r'(data-[\w-]+)=', attrs)
                if data_key:
                    selector += f"[{data_key.group(1)}='{data.group(1)}']"

        if selector and name:
            interactions.append({
                "name": name[:40],
                "action": "click",
                "selector": selector,
                "effect": f"{name} が実行される",
            })

    # <a> タグ（内部リンク・ホットスポット）
    for match in re.finditer(
        r'<a([^>]*)>(.*?)</a>', html, re.DOTALL
    ):
        attrs = match.group(1)
        inner = re.sub(r"<[^>]+>", "", match.group(2)).strip()

        classes = re.search(r'class=["\']([^"\']+)["\']', attrs)
        id_attr = re.search(r'id=["\']([^"\']+)["\']', attrs)
        href = re.search(r'href=["\']([^"\']+)["\']', attrs)
        aria = re.search(r'aria-label=["\']([^"\']+)["\']', attrs)

        # 外部リンク・フッターリンクはスキップ
        if href and (href.group(1).startswith("http") or
                     href.group(1).startswith("/archive/logs") or
                     href.group(1) in ("/about", "/privacy-policy", "/contact",
                                        "/terms", "/sitemap")):
            continue

        selector = ""
        name = inner or (aria.group(1) if aria else "")
        if id_attr:
            selector = f"#{id_attr.group(1)}"
        elif classes:
            cls_list = classes.group(1).split()
            selector = "." + cls_list[0]

        if selector and name and len(name) < 50:
            interactions.append({
                "name": name[:40],
                "action": "click",
                "selector": selector,
                "effect": f"{href.group(1) if href else selector} へ遷移する",
            })

    # 重複除去
    seen = set()
    unique = []
    for item in interactions:
        key = item["selector"]
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique[:10]  # 最大10件


def sync(verbose: bool = True) -> None:
    if not LORE_PATH.exists():
        print(f"ERROR: {LORE_PATH} が見つかりません。")
        sys.exit(1)

    md_text = LORE_PATH.read_text(encoding="utf-8")
    lore_map = parse_lore_from_md(md_text)

    existing = load_json(HOTSPOTS_PATH, {"viewport": {"width": 393, "height": 852}, "pages": {}})
    existing_pages = existing.get("pages", {})

    new_pages: dict = {}

    for route, lore_data in lore_map.items():
        # テンプレートファイルを探す
        template_name = ROUTE_TO_TEMPLATE_ALT.get(route, ROUTE_TO_TEMPLATE.get(route, ""))
        template_path = TEMPLATES / template_name if template_name else None

        # 代替テンプレートも試す
        if template_path and not template_path.exists():
            alt = ROUTE_TO_TEMPLATE_ALT.get(route, "")
            if alt:
                template_path = TEMPLATES / alt

        interactions = scan_interactions(template_path) if template_path else []

        # 既存のinteractionsがあれば保持（手動追記分を消さない）
        if route in existing_pages:
            old_interactions = existing_pages[route].get("interactions", [])
            # 既存のセレクタに含まれていないものだけ追加
            existing_selectors = {i["selector"] for i in old_interactions}
            for new_item in interactions:
                if new_item["selector"] not in existing_selectors:
                    old_interactions.append(new_item)
            interactions = old_interactions

        new_pages[route] = {
            "room_name": lore_data.get("room_name", ""),
            "lore": lore_data.get("lore", ""),
            "narrative_purpose": lore_data.get("narrative_purpose",
                existing_pages.get(route, {}).get("narrative_purpose", "")),
            "interactions": interactions,
        }

    result = {
        "viewport": existing.get("viewport", {"width": 393, "height": 852}),
        "note": "kyoukai-world.md から自動生成。loreの更新はkyoukai-world.mdのみ行う。",
        "pages": new_pages,
    }

    HOTSPOTS_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if verbose:
        print(f"kyoukai_hotspots.json を更新しました（{len(new_pages)} ページ）")
        for route, data in new_pages.items():
            n = len(data.get("interactions", []))
            print(f"  {route} [{data['room_name']}] — インタラクション {n} 件")


if __name__ == "__main__":
    sync(verbose=True)
