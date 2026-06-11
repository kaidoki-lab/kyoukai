# KYOUKAI project instructions

## 実装完了時の必須処理

- Central OS由来の実装指示には、必ず元企画IDを保持する。
- 実装と検証が完了したら `complete_implementation.py` を実行し、完了事象をCentral OSへ記録する。
- 対応する実装タスクが存在する場合は、同コマンドで `done`・実行履歴・成果物・検証結果を同期する。
- `--changed-file` には今回変更した関連ファイルだけを明示し、既存の無関係な差分を含めない。
- ユーザーが明示的に止めない限り、実装完了後は関連差分をコミットし、`main`へプッシュしてVercel本番反映を確認する。
- コミット・プッシュ・本番反映のいずれかに失敗した場合は、完了扱いにせず原因を報告して再試行する。

## 完了コマンド例

```powershell
python complete_implementation.py `
  --plan-id plan-YYYYMMDDHHMMSS-NN `
  --title "実装タイトル" `
  --target-page /target `
  --summary "実装内容" `
  --artifact path/to/file `
  --verification "テスト成功" `
  --changed-file path/to/file `
  --changed-file complete_implementation.py `
  --commit-message "Implement feature" `
  --push
```
