# Central OS 隔離リスト

切り離し日: 2026-06-18  
状態: `/central` ルート削除済み → URLは404。他ファイルは未削除。

影響確認後、以下を全削除する。

---

## テンプレート / スタイル

- `templates/central.html`
- `static/central.css`

## Pythonモジュール（Central OS専用）

- `implementation_events.py`
- `auto_generator.py` ※ `/codex` と daimyojin でも使用中 → 削除前に確認

## main.py 内の削除対象

- `from implementation_events import load_events, planner_completed_context`（line 34）
- `CENTRAL_OS_DIR` 以降の定数ブロック（line 751〜835付近）
- `run_ai_planner()` 関数とその関連関数群
- API エンドポイント群:
  - `GET/POST /api/central-os`
  - `POST /api/update-proposals/run`
  - `POST /api/update-proposals/{id}/status`
  - `POST /api/plan-proposals/run`
  - `POST /api/plan-proposals/{id}/status`
  - `GET /api/implementation-events/archive`
  - `POST /api/implementation-events/archive`
  - `POST /api/implementation-tasks/run`
  - `POST /api/implementation-tasks/{id}/status`
  - `# /central route removed` コメント行

## データディレクトリ（ローカルのみ・Vercel無関係）

- `central-os/`（全サブディレクトリ含む）

---

## 削除前チェック

- [ ] 本番サイト（void-kyoukai.net）で `/central` が404になっていることを確認
- [ ] 本番サイトの他のページ（/, /observation 等）が正常に動いていることを確認
- [ ] `auto_generator.py` が `/codex` または daimyojin に必要かどうか確認
