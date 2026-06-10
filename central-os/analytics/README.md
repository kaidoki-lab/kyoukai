# YouTube Analytics セットアップ手順

## 必要なもの

1. Google Cloud Console でプロジェクトを作成
2. 以下のAPIを有効化:
   - YouTube Data API v3
   - YouTube Analytics API
3. OAuth 2.0 クライアントID（デスクトップアプリ）を作成
4. クライアントシークレットJSON をダウンロードして配置

## 配置場所

```
credentials/
  youtube_client_secret.json   ← Google Cloud からダウンロード
  youtube_token.json            ← 初回認証後に自動生成される
```

## パッケージインストール

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## 実行順序

```bash
# 1. データ取得（初回はブラウザで認証が開く）
python central-os/analytics/youtube_fetcher.py

# 2. 分析・スコアリング
python central-os/analytics/youtube_analyzer.py

# 3. 次のショート案を生成（GROQ_API_KEY または OPENROUTER_API_KEY 必要）
python central-os/analytics/youtube_prompt_builder.py
```

## 生成ファイル

| ファイル | 内容 |
|---|---|
| `youtube_shorts.json` | 動画別生データ |
| `youtube_shorts.csv` | 同上（CSV形式） |
| `youtube_summary.json` | 分析済みサマリー（Central OSが読む） |
| `youtube_next_shorts.json` | AIが提案するショート案10本 |

## Central OS での確認

`/central` の「YouTube分析」セクションで最終取得日時・上位動画・次のショート案が確認できる。

## セキュリティ

- `credentials/` は `.gitignore` に含まれており Git にはコミットされない
- APIキーは `.env` ファイルで管理する（`GROQ_API_KEY`, `OPENROUTER_API_KEY`）
