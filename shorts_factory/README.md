# KYOUKAI Shorts Factory

KYOUKAI制作作業をYouTube Shorts候補へ変換するローカル量産ラインです。
動画編集ソフトではなく、`bat起動 -> 録画 -> 停止 -> 候補生成` を簡単に固定するための補助システムです。

## 使い方

1. OBSの録画保存先を `shorts_factory/input_videos/` に設定する
2. OBS WebSocketを有効化する
3. `config.json` の `obs.password` を自分のOBS WebSocketパスワードに合わせる
4. 必要なら `input_audio/` にBGM音源、`qr/` にQR画像を置く
5. `start_kyoukai_record.bat` を実行する
6. KYOUKAI制作作業を録画する
7. `stop_kyoukai_record.bat` を実行する

停止後に `main.py` が実行され、`output_shorts/` にShorts候補、`output_meta/` に投稿用テキストが出ます。

## フォルダ

- `input_videos/`: OBS録画素材の保存先
- `input_audio/`: 固定BGMの置き場。空ならBGMなしで生成
- `qr/`: QR画像の置き場。空ならQRなしで生成
- `output_shorts/`: 完成したShorts候補。自動削除しない
- `output_meta/`: 投稿用タイトル、説明、固定コメント。自動削除しない
- `recordings_archive/`: 処理済み録画素材の退避先
- `logs/`: 処理ログ、OBS制御ログ、削除ログ
- `temp/`: 一時ファイル置き場

## FFmpeg

動画変換にはFFmpegとFFprobeが必要です。
PATHに入っていない場合は `config.json` に直接指定してください。

```json
{
  "video": {
    "ffmpeg_path": "C:\\ffmpeg\\bin\\ffmpeg.exe",
    "ffprobe_path": "C:\\ffmpeg\\bin\\ffprobe.exe"
  }
}
```

## OBS

`start_kyoukai_record.bat` はOBSを起動し、`tools/obs_control.js` からobs-websocket v5へ `StartRecord` を送ります。
`stop_kyoukai_record.bat` は `StopRecord` を送り、その後 `main.py` を実行します。

OBS起動時にクラッシュ回復ダイアログが出た場合は、セーフモードではなく通常モードを選んでください。

## 生成ルール

- 1本の録画素材から最大5本の候補を作成
- 初期実装では見どころAI判定はしない
- 一定間隔で15秒切り出し
- 1080x1920の9:16へ中央クロップ
- BGMがあれば合成
- QR画像があれば右下に合成
- テロップは付けない

## 録画画面

OBS側の録画元は1920x1080のフル画面です。横長の作業画面を切らずに保存し、Shorts候補を作る時だけ1080x1920へ中央クロップします。

録画サイズは `config.json` の以下で変更できます。

```json
{
  "obs": {
    "recording_width": 1920,
    "recording_height": 1080,
    "recording_fps": 30
  }
}
```

## 切り抜き位置

### 録画中にマークする

録画中に「ここをShorts候補にしたい」と思ったら、左手で `Ctrl + Shift` を約0.35秒押し続けます。

```text
start_kyoukai_record.bat
  ↓ 作業する
Ctrl + Shift
  ↓ 別の見どころでもう一度マーク
Ctrl + Shift
  ↓
stop_kyoukai_record.bat
```

マークに成功すると短い高音が2回鳴ります。キーを離すまで追加マークされないため、押し続けても1回だけ記録されます。録画していない時や失敗時は低い音が鳴ります。

ホットキー監視は `start_kyoukai_record.bat` の録画開始後にバックグラウンドで起動し、`stop_kyoukai_record.bat` で自動終了します。フォルダを開いてBATを毎回探す必要はありません。

マーク地点の10秒前から30秒を切り抜きます。10秒前という値は次の設定で変更できます。

```json
{
  "video": {
    "short_length_sec": 30,
    "marker_pre_roll_sec": 10
  }
}
```

マークが1件以上ある場合は、マーク位置が自動切り抜きや手動時刻より優先されます。

従来の `mark_kyoukai_clip.bat` も予備として利用できます。

### config.jsonで時刻を指定する

`config.json` の `video.manual_cut_points` に開始時刻を指定できます。

```json
{
  "video": {
    "short_length_sec": 15,
    "manual_cut_points": [
      "00:30",
      "12:15",
      "37:40",
      "01:04:20"
    ]
  }
}
```

- `00:30` は30秒地点
- `12:15` は12分15秒地点
- `01:04:20` は1時間4分20秒地点
- 数字の秒数指定も可能
- 空配列 `[]` の場合は従来通り等間隔で自動切り抜き
- 各指定時刻から `short_length_sec` 秒を切り抜く

## 投稿用メタ

`status.json` の `next_devlog_number` から `devlog_001` のような連番を作ります。
各候補に対応する投稿用テキストは `output_meta/devlog_XXX.txt` に出力されます。

## 自動削除

`main.py` 起動時に、3日以上古い以下のファイルを削除します。

- `input_videos/`
- `recordings_archive/`
- `temp/`

削除前に `logs/cleanup.log` へ記録します。
`output_shorts/`、`output_meta/`、`logs/`、`config.json`、`status.json`、`input_audio/`、`qr/` は削除しません。

## 録画しないもの

GA4、Google Search Console、AdSense、メール、銀行、個人情報、ログイン情報、APIキー、パスワード、住所や氏名が映る画面は録画しないでください。
