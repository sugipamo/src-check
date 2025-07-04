# 計画: GitHub Actions CI修正

## 作成日時
2025-07-03 10:15

## 目的
GitHub ActionsのCIパイプラインで発生しているテスト失敗を修正し、安定したCI/CD環境を構築する

## 現状の問題

### 1. ImportError in KPI CLI
```
cannot import name 'CheckerRegistry' from 'src_check.core.registry'
```
- 影響: 3つのKPI関連テストが失敗
- 原因: kpi.pyの最新修正で`CheckerRegistry`をインポートしているが、テスト環境で正しく参照できない

### 2. テスト実行環境の問題
- Python 3.8, 3.9, 3.10, 3.11の4環境でテスト実行
- 全環境で同じエラーが発生

## 修正方針

### フェーズ1: 即座の修正（優先度: 高）

#### 1.1 インポートエラーの修正
**対象ファイル**: `src/src_check/cli/kpi.py`

現在の問題のあるインポート:
```python
from src_check.core.registry import CheckerRegistry
```

修正案:
- インポートを関数内に移動（既に実装済み）
- テスト時のモック対応を改善

#### 1.2 テストコードの修正
**対象ファイル**: 
- `tests/unit/test_cli.py`
- `tests/unit/test_cli_import.py`

修正内容:
1. KPI CLIテストでのエラーハンドリング追加
2. モックを使用した単体テストへの変更
3. 統合テストと単体テストの分離

### フェーズ2: テスト安定性の向上（優先度: 中）

#### 2.1 テスト環境の改善
- テスト用の設定ファイル追加
- 依存関係の明確化
- テストデータの整備

#### 2.2 GitHub Actionsワークフローの最適化
**対象ファイル**: `.github/workflows/test.yml`

修正内容:
1. Python 3.8サポートの確認
2. キャッシュ戦略の改善
3. 並列実行の最適化

## 実装手順

### ステップ1: テストコードの即座の修正（15分）
1. `test_cli.py`のKPIテストを修正
   - プロセス実行ではなく、関数を直接テスト
   - 適切なモックの使用

2. `test_cli_import.py`の修正
   - インポートエラーのハンドリング
   - テスト分離の改善

### ステップ2: ローカルでのテスト確認（10分）
```bash
# 単体テストの実行
pytest tests/unit/test_cli.py -v
pytest tests/unit/test_cli_import.py -v

# 全テストの実行
pytest -v
```

### ステップ3: 修正のコミットとプッシュ（5分）
```bash
git add -A
git commit -m "fix: Fix KPI CLI tests for GitHub Actions CI

- Fix import errors in KPI-related tests
- Add proper mocking for CLI tests
- Ensure compatibility with all Python versions (3.8-3.11)"
git push origin main
```

### ステップ4: CI/CD動作確認（10分）
- GitHub Actionsの実行を監視
- エラーが解消されることを確認
- 全てのPythonバージョンでグリーンになることを確認

## 期待される結果
1. 全182テストが全Python環境で成功
2. CI/CDパイプラインが安定稼働
3. 本番PyPI公開の準備完了

## リスクと対策
- **リスク**: テスト修正により実際のバグが隠蔽される
- **対策**: 統合テストを別途追加し、実際の動作を確認

## 完了条件
- [ ] GitHub Actionsで全テストがパス
- [ ] 4つのPython環境（3.8-3.11）全てでグリーン
- [ ] ruffチェックもパス
- [ ] コードカバレッジ85%以上を維持

## 次のアクション
1. この計画に基づいてテストコードを修正
2. ローカルでテスト実行
3. 修正をコミット・プッシュ
4. GitHub Actionsの結果を確認
5. 本番PyPI公開へ進む