#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KYOUKAI OBSパック 商品ページ文章16本生成"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_packs import ROOMS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, 'listings')
KYOUKAI_URL = 'https://kyoukai.vercel.app'

# ───────────────────────────────────────────────
# 部屋別 一言コピー（タイトル用）
# ───────────────────────────────────────────────
CATCHCOPY = {
    'observation': '観測は続いている',
    'hyougi': '発言者は不明のまま',
    'null': '崩壊は止まらない',
    'observer': '見ていたのはあなただった',
    'exit': '境界を越える途中',
    'archive': '削除されたはずの記録',
    'ma': '存在はここにある',
    'daimyojin': '願いは観測されている',
    'gokuraku': '奥への扉はまだ開かない',
    'particles': '意味より先に運動がある',
    'ripple': '触れると世界が応答する',
    'kanrinin': 'しばらくお待ちください',
    'namahage': '泣く子はいねぇか',
    'matsuri': '奉納は継続されている',
    'fukashitsu': '孵化まで観測を続ける',
    'typhoon-news': '続報をお待ちください',
}

# ───────────────────────────────────────────────
# 部屋別 世界観記述（data/kyoukai_world.md 各部屋詳細の要約）
# ───────────────────────────────────────────────
WORLDVIEW = {
    'observation': (
        '観測域は、KYOUKAIの中でもっとも活動が多い部屋。生命体の観測ログが絶えず積み上がっていく。'
        'ログは感情を持たない。だが、それを見ていると何かを感じる。観測対象が誰なのかは、最後まで語られない。'
    ),
    'hyougi': (
        '評議録には、誰かが記した議事の断片が残されている。発言者は不明。議題も結論も曖昧なまま、'
        '複数の声だけが記録されていく。合意しているのか、対立しているのかは判別できない。'
    ),
    'null': (
        '崩落域は、世界が崩壊していく過程だけを記録している。データはある。だが何のデータかはわからない。'
        'ページとして機能しているが、触れるほどに状態が悪化していく。長く留まると、自分が何をしていたのかも曖昧になる。'
    ),
    'observer': (
        '逆観測室は、KYOUKAIの最深部。ここで観測する側とされる側が逆転する。'
        '静かに、そっと、こう告げられる。あなたはずっと観測されていた。'
    ),
    'exit': (
        '境界域は、外へ出るための接続口に見える場所。だが実際には、内部と外部、複数の記録が混線する通路にすぎない。'
        '進んでいるつもりでも、見ているのは境界を越えようとしていた誰かの断片。終わりのようで、終わりではない。'
    ),
    'archive': (
        '記録室には、感情を排した観測記録が積み上がっている。日付、ID、内容だけの羅列。'
        '感情は排除されているはずなのに、読むと何かが生まれる。削除されたはずの記録が、まだそこに残っている気配がある。'
    ),
    'ma': (
        '悪魔の間は、逆観測室の奥にある隠し部屋。玉座に座る存在は、訪問を重ねるたびに態度を変えていく。'
        '最初は拒絶的だが、何度も訪れるうちに、その存在は少しずつ訪問者を受け入れ始める。'
    ),
    'daimyojin': (
        'AI大明神は、信仰と機械が混ざり合った祈願装置。神社と端末が同じ構造物の中にある。'
        '占いのように見えるが、処理されているのが願いなのか観測結果なのかは、最後まで明かされない。'
    ),
    'gokuraku': (
        '極楽域は、引き出しとスピーカーと祠が積み上がった奥の部屋。「極楽」という言葉は、ここでは明るく響かない。'
        '過剰な収納と音響装置が、記憶の保管庫にも、通路にも見える。'
    ),
    'particles': (
        '粒子観測は、無数の粒子群をただ見つめる部屋。画面内の運動と反応がまずあり、意味はその後からやってくる。'
        '衝突を避け、方向を変え、群れていく粒子たちに、明確な目的は与えられていない。'
    ),
    'ripple': (
        '波紋域は、触れることで世界が応答する部屋。ドットが波紋の順に色を変えていくが、'
        '一点だけ、その命令に完全には従わない異常な反応が残り続ける。'
    ),
    'kanrinin': (
        '管理人室は、KYOUKAIの管理施設。昭和から平成初期のラブホテル受付を思わせる空間に、'
        '鍵ボックス、消滅の鍵、管理日誌が並んでいる。管理人本人の姿は、決して見えない。'
    ),
    'namahage': (
        'なまはげの部屋では、赤く光る瞳がこちらを見つめている。タップ、長押し、ダブルタップに応じて瞳の反応が変わり、'
        '長押しを続けると起動シーケンスが進行していく。逃げる場所はない。'
    ),
    'matsuri': (
        '棒入れ祭は、豊穣信仰の奉納儀式を再現した部屋。棒を穴へ繰り返し沈めていくと、'
        '土煙と紙吹雪が舞い、やがて奉納が完了する。人物は誰も描かれていない。'
    ),
    'fukashitsu': (
        '卵部屋では、ピンク色の孵化装置の中で粒子群がゆっくりと色を帯びていく。'
        '栄養、酸素、温度。三つの操作を重ねるごとに、卵の中の何かが観測を続けている。'
    ),
    'typhoon-news': (
        '台風ニュースは、ニュース番組の顔をした速報室。画面には速報帯と警戒表示が流れ続けるが、'
        '台風の名前だけが「後ほど連絡します」「お母さんに聞いて」といった、日常の保留語に置き換わっている。'
    ),
}

# ───────────────────────────────────────────────
# 部屋別タグ（5個ずつ）
# ───────────────────────────────────────────────
ROOM_TAGS = {
    'observation': ['観測', '記録映像', 'ログ演出', 'KYOUKAI', '不穏系配信'],
    'hyougi': ['議事録風', 'タイプライター', 'KYOUKAI', '不穏系配信', 'テキスト演出'],
    'null': ['グリッチ', '崩壊演出', 'KYOUKAI', '不穏系配信', 'ノイズ素材'],
    'observer': ['逆観測', '最深部', 'KYOUKAI', '不穏系配信', 'パルス演出'],
    'exit': ['接続演出', 'ローディング', 'KYOUKAI', '不穏系配信', '境界'],
    'archive': ['アーカイブ風', 'ファイル演出', 'KYOUKAI', '不穏系配信', '記録映像'],
    'ma': ['存在感演出', '呼吸モーション', 'KYOUKAI', '不穏系配信', '玉座'],
    'daimyojin': ['祈願演出', '回路デザイン', 'KYOUKAI', '不穏系配信', '神託'],
    'gokuraku': ['音響演出', '記憶の部屋', 'KYOUKAI', '不穏系配信', 'グロー演出'],
    'particles': ['パーティクル', '粒子演出', 'KYOUKAI', '不穏系配信', '観測系'],
    'ripple': ['波紋演出', 'リップル', 'KYOUKAI', '不穏系配信', '応答演出'],
    'kanrinin': ['レトロ演出', '受付風', 'KYOUKAI', '不穏系配信', 'ノイズ素材'],
    'namahage': ['民俗系', '瞳演出', 'KYOUKAI', '不穏系配信', 'ホラー系配信'],
    'matsuri': ['祭り演出', '奉納', 'KYOUKAI', 'ネタ配信', '紙吹雪演出'],
    'fukashitsu': ['孵化演出', '粒子観測', 'KYOUKAI', '不穏系配信', 'パステル演出'],
    'typhoon-news': ['ニュース風', '速報テロップ', 'KYOUKAI', 'ネタ配信', 'ティッカー演出'],
}

COMMON_TAGS = ['OBS', '配信', 'オーバーレイ', '待機画面', '配信素材']

PRICE = 300

# ───────────────────────────────────────────────
# 禁止ワード
# ───────────────────────────────────────────────
FORBIDDEN_WORDS = [
    '解説', 'わかりやすく', '入門', '方法', 'やり方', 'コツ', '裏技',
    'チャンネル登録', 'チャレンジ', 'ランキング', 'おすすめ',
    '元気', '前向き', '感動', 'おめでとう',
]


def make_title(room):
    return f"{room['name']} OBS素材パック ── {CATCHCOPY[room['id']]}"


def make_worldview_part(room):
    """世界観パート: 冒頭の世界観一文 + 同梱3点の説明（禁止ワード検査対象）"""
    intro = WORLDVIEW[room['id']]
    body = f"""{intro}

【同梱内容】3点

  01_waiting / waiting.html
    待機画面。{room['label']}の状態を表示し続ける。
    配信前、ゲームロード中、場面転換に使用する。

  02_brb / brb.html
    離席中画面。「{room['brb_main']}」というメッセージが表示される。
    離席時、準備中、一時中断時に使用する。

  03_lower-third / lower_third.html
    ローワーサード（名前テロップ）。透過背景。
    他の素材の上に重ねてオーバーレイとして使用する。"""
    return body


def make_setup_part():
    return """【OBS設定方法】

  1. OBS Studio を開く
  2. ソース → ＋ → ブラウザ を追加
  3. 「ローカルファイル」にチェックを入れる
  4. 各 .html ファイルを指定する
  5. 幅: 1920  /  高さ: 1080 に設定する

  ローワーサードの名前・肩書きは lower_third.html 内の該当箇所を
  書き換えることで変更できる。"""


def make_env_part():
    return """【動作環境】

  OBS Studio 29以降推奨
  インターネット接続不要 / 完全ローカル動作"""


def make_terms_part():
    return """【利用規約】

  個人・商用配信どちらでも使用可
  再配布・転売 禁止
  改変は個人使用の範囲で自由"""


def make_footer():
    return f"""KYOUKAI ─ 境界
{KYOUKAI_URL}"""


def make_description(room):
    parts = [
        make_worldview_part(room),
        make_setup_part(),
        make_env_part(),
        make_terms_part(),
        make_footer(),
    ]
    return '\n\n'.join(parts)


def make_tags(room):
    return COMMON_TAGS + ROOM_TAGS[room['id']]


def make_markdown(room):
    title = make_title(room)
    description = make_description(room)
    tags = make_tags(room)
    lines = []
    lines.append(f"# {title}")
    lines.append('')
    lines.append('## 商品説明文')
    lines.append('')
    lines.append(description)
    lines.append('')
    lines.append('## タグ')
    lines.append('')
    lines.append(' / '.join(tags))
    lines.append('')
    lines.append('## 価格')
    lines.append('')
    lines.append(f"{PRICE}円")
    lines.append('')
    return '\n'.join(lines)


def check_forbidden(room, title, worldview_part):
    """タイトルと世界観パート（冒頭〜同梱内容まで）に禁止ワードが含まれないか検査"""
    hits = []
    check_text = title + '\n' + worldview_part
    for word in FORBIDDEN_WORDS:
        if word in check_text:
            hits.append(word)
    return hits


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("商品ページ文章 生成開始...")

    all_pass = True
    for room in ROOMS:
        if room['id'] not in WORLDVIEW or room['id'] not in CATCHCOPY or room['id'] not in ROOM_TAGS:
            print(f"  NG {room['id']}: データ未定義")
            all_pass = False
            continue

        title = make_title(room)
        worldview_part = make_worldview_part(room)
        md = make_markdown(room)

        out_path = os.path.join(OUT_DIR, f"{room['id']}.md")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(md)

        hits = check_forbidden(room, title, worldview_part)
        if hits:
            print(f"  NG {room['name']} ({room['id']}): 禁止ワード検出 {hits}")
            all_pass = False
        else:
            title_len_ok = len(title) <= 40
            mark = "OK" if title_len_ok else "WARN(title>40字)"
            print(f"  {mark} {room['name']} ({room['id']}) title_len={len(title)}")

    print(f"\n生成完了 {len(ROOMS)}部屋 -> {OUT_DIR}")

    if all_pass:
        print("禁止ワード検査: 全件 PASS")
    else:
        print("禁止ワード検査: NG あり。上記を確認すること")

    return all_pass


if __name__ == '__main__':
    ok = main()
    sys.exit(0 if ok else 1)
