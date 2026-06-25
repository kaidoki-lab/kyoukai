# KYOUKAI Shorts Factory

KYOUKAI制作・探索の様子をYouTube Shorts候補に変換するローカル量産ラインです。
動画編集ソフトではなく、`bat起動 -> シナリオ生成 -> 自動巡回・録画` を簡単に固定するための補助システムです。

## 使い方（日常運用）

1. `auto_browse.bat` を実行する
2. 自動でシナリオが生成され、Chromiumが起動してKYOUKAI内を自動巡回・録画する
3. クリップごとに `sessions/<日付>/raw_clips/` へ `.webm` で保存される

これだけで完結します。OBSなど別アプリの起動・録画開始/停止操作は不要です。

## 仕組み

- `generate_scenario.py`: `data/kyoukai_world.md`（ロア）と `data/city_locations.json`（CITY街区データ）からその日の巡回ルートとブラウズ手順（スクロール・マウス移動・ホットスポットクリック）を生成する。直前のルートとは絶対に被らない
- `sync_hotspots.py`: `templates/*.html` と `data/city_locations.json` をスキャンして `kyoukai_hotspots.json`（各ページのクリック可能要素一覧）を自動更新する。`generate_scenario.py` の実行時に内部で自動的に呼ばれる
- `auto_browse.py`: Playwright で携帯ブラウザ（iPhone相当の縦長ビューポート）を起動し、生成されたシナリオに沿ってKYOUKAI内を巡回しながらクリップ単位で録画する

## ルート

`generate_scenario.py` 内の `ROUTE_SETS` に定義されている。

| ルート | 内容 |
|---|---|
| Route-A 深層 | /observer, /ma, /null, /archive |
| Route-B 境界 | /exit, /signal, /outside, /hyougi |
| Route-C 記録 | /archive, /hyougi, /observation, /observer |
| Route-D 入口巡回 | /, /signal, /null, /exit |
| Route-E 街区 | /city/city-001, /city/city-002, /city/city-005, /city/city-004 |
| Route-F 路地裏 | /city/city-001, /city/city-009, /city/city-003, /city/city-010 |

CITY側の `/altar` および奉納街周辺（city-006〜008）はサイト側が変更中のため、ルートには含めていません。

## フォルダ

- `sessions/<日付>/`: その日のシナリオ・収録クリップ（`raw_clips/*.webm`）
- `kyoukai_hotspots.json`: 各ページのクリック可能要素の自動生成データ（手で直接編集しない。ロアの更新は `data/kyoukai_world.md`、CITYの導線は `data/city_locations.json` 側で行う）
- `logs/`: 処理ログ（`process.log`, `cleanup.log`）
- `temp/`: 一時ファイル置き場

## 録画した素材をShorts候補に変換する（任意・手動）

`auto_browse.py` の出力はそのままだと `sessions/<日付>/raw_clips/` に置かれたクリップ単位の動画です。
QR合成・BGM合成・複数候補への切り出しをしたい場合は、対象の動画を `input_videos/` に移してから `main.py` を実行してください。

```
python main.py
```

- `output_shorts/`: 完成したShorts候補。自動削除しない
- `output_meta/`: 投稿用タイトル・説明・固定コメント。自動削除しない

### FFmpeg

動画変換には `tools/ffmpeg/` 同梱のFFmpeg/FFprobeを使用する。パスは `config.json` の `video.ffmpeg_path` / `ffprobe_path` で指定。

### 切り出し設定

```json
{
  "video": {
    "short_length_sec": 30,
    "candidates_per_video": 5,
    "manual_cut_points": []
  }
}
```

- `manual_cut_points` に `"00:30"` のような時刻を指定すると、その時刻から `short_length_sec` 秒を切り出す
- 空配列 `[]` の場合は等間隔で自動切り出し

## 投稿用メタ（任意）

`finished_shorts/` に手動編集済みの動画を置いて `generate_meta.bat` を実行すると、固定テンプレート（`generate_meta.py` 内の `TITLES` / `FIXED_COMMENTS`）からランダムにタイトル・説明・固定コメントを組み立てる。AIもCentral OSも使わない。
`status.json` の `next_devlog_number` から `devlog_001` のような連番を振る。

## 自動削除

`main.py` 起動時に、3日以上古い以下のファイルを削除する。

- `input_videos/`
- `recordings_archive/`
- `temp/`

削除前に `logs/cleanup.log` へ記録する。
`output_shorts/`、`output_meta/`、`logs/`、`config.json`、`status.json`、`input_audio/`、`qr/`、`sessions/` は削除しない。

## 録画しないもの

GA4、Google Search Console、AdSense、メール、銀行、個人情報、ログイン情報、APIキー、パスワード、住所や氏名が映る画面は録画しないでください。
