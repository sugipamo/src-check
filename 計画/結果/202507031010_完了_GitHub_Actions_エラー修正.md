# 修正依頼: GitHub Actions エラー修正

## 作成日時
2025-07-03 10:10

## 概要
GitHub ActionsでCI/CDパイプラインが失敗しています。主に以下の問題が発生：

1. **KPIテストの失敗** - ImportError: cannot import name 'CheckerRegistry' from 'src_check.core.registry'
2. **Python 3.8でのテスト失敗** - ruffの実行エラー

## 詳細な問題

### 1. KPI CLIテストの失敗（Python 3.10, 3.11）
```
FAILED tests/unit/test_cli.py::test_kpi_cli_basic_execution
FAILED tests/unit/test_cli_import.py::TestKPICLI::test_kpi_main_basic_execution
FAILED tests/unit/test_cli_import.py::TestKPICLI::test_kpi_main_with_checkers_filter

Error: cannot import name 'CheckerRegistry' from 'src_check.core.registry'
```

**原因**: 最新のコード変更（kpi.pyの修正）がテストに反映されていない

### 2. Python 3.8でのruff実行エラー
Python 3.8環境でruffが正しく動作していない可能性

## 修正案

### 1. KPIテストの修正
`tests/unit/test_cli.py`と`tests/unit/test_cli_import.py`のKPI関連テストを更新：
- ハードコードされた出力を期待しているテストを修正
- 実際のKPI計算ロジックに対応したモックを使用

### 2. GitHub Actionsワークフローの更新
`.github/workflows/test.yml`の修正：
- Python 3.8のサポートを確認（または削除）
- ruffのバージョン固定
- 依存関係のインストール順序の最適化

### 3. 緊急度
**高** - PyPI公開前に修正が必要

## 対応タスク
1. [ ] テストコードの修正（KPI関連）
2. [ ] GitHub Actionsワークフローの調整
3. [ ] ローカルでのテスト実行確認
4. [ ] 修正後のCI/CD動作確認

## 備考
- TestPyPIへの公開は成功しているが、CIが失敗している状態
- 本番PyPI公開前に必ず修正が必要