# src-check

**Pythonコード品質分析・KPIスコアリングシステム**

src-checkは、Pythonプロジェクトの品質を包括的に分析し、定量的な評価を提供するツールです。10種類のチェッカーによる詳細な問題検出と、4軸評価によるKPIスコアリングで、コード品質の継続的な改善をサポートします。

## 🚀 特徴

- **10種類の品質チェッカー**: セキュリティ、アーキテクチャ、コード品質、テスト品質など多角的な分析
- **KPIスコアリング**: 機能性・保守性・信頼性・効率性の4軸で0-100点の定量評価
- **詳細なレポート**: 問題箇所と改善提案を含む実用的なフィードバック
- **高速実行**: 効率的な並列処理により大規模プロジェクトにも対応
- **柔軟な設定**: プロジェクトに応じたカスタマイズが可能

## 📦 インストール

### pipでのインストール（予定）

```bash
pip install src-check
```

### 開発環境でのセットアップ

```bash
# リポジトリのクローン
git clone https://github.com/src-check/src-check
cd src-check

# 依存関係のインストール（uvを使用）
uv sync --dev

# または通常のpipを使用
pip install -e ".[dev]"
```

## 🔧 使い方

### 基本的な使い方

```bash
# カレントディレクトリを分析
src-check

# 特定のディレクトリやファイルを分析
src-check src/ tests/

# 詳細な出力を表示
src-check --verbose

# 特定のチェッカーのみ実行
src-check --checkers security,code_quality
```

### KPIスコアの計算

```bash
# KPIスコアのみを表示
src-check-kpi

# JSON形式で出力
src-check-kpi --format json

# 特定のパスを分析
src-check-kpi src/
```

### 実行例と出力

```bash
$ src-check src/

🔍 Running src-check analysis...

Security Issues:
  src/api/auth.py:45 [SEC001] Hardcoded password detected
  src/utils/crypto.py:23 [SEC003] Weak cryptographic algorithm (MD5)

Code Quality Issues:
  src/models/user.py:67 [CQ001] Function too complex (cyclomatic complexity: 15)
  src/services/data.py:89 [CQ003] Duplicate code block detected

Architecture Issues:
  src/controllers/admin.py:12 [ARCH001] Circular dependency detected
  src/models/__init__.py:5 [ARCH003] God class detected (>500 lines)

Total issues found: 23
- Critical: 3
- High: 8
- Medium: 10
- Low: 2

✨ Analysis complete in 2.3s
```

## 🔍 チェッカー一覧

### 1. SecurityChecker
セキュリティ脆弱性を検出します。
- ハードコードされたパスワードや秘密鍵
- SQLインジェクションのリスク
- 安全でない乱数生成
- 弱い暗号化アルゴリズム

### 2. CodeQualityChecker
コード品質の問題を検出します。
- 高い循環的複雑度
- 長すぎる関数やクラス
- 重複コード
- ネストが深いコード

### 3. ArchitectureChecker
アーキテクチャの問題を検出します。
- 循環依存
- レイヤー違反
- 神クラス（責務過多）
- 不適切なモジュール構造

### 4. TestQualityChecker
テストの品質を評価します。
- テストカバレッジ不足
- アサーションなしのテスト
- テストの重複
- 不適切なモック使用

### 5. DocumentationChecker
ドキュメントの品質をチェックします。
- docstringの欠如
- 不完全なdocstring
- パラメータ説明の不足
- 例の欠如

### 6. TypeHintChecker
型ヒントの充実度を評価します。
- 型アノテーションの欠如
- 不完全な型定義
- Any型の過度な使用
- 型の不整合

### 7. PerformanceChecker
パフォーマンスの問題を検出します。
- ループ内での不変式
- 非効率な文字列結合
- 不要な型変換
- 深いネスト構造

### 8. DependencyChecker
依存関係の健全性をチェックします。
- 循環依存
- 未使用の依存関係
- バージョン未指定
- 開発/本番依存の混在

### 9. LicenseChecker
ライセンスの整合性を確認します。
- LICENSEファイルの有無
- 依存関係とのライセンス互換性
- コピーライトヘッダー
- ライセンス表記の一貫性

### 10. DeprecationChecker
廃止予定の機能使用を検出します。
- Python標準ライブラリの廃止予定API
- 古い文字列フォーマット
- 非推奨のimport方法
- レガシーな書き方

## ⚙️ 設定

### 設定ファイル（.src-check.yaml）

```yaml
# チェッカーの有効/無効設定
checkers:
  security:
    enabled: true
  code_quality:
    enabled: true
    options:
      max_complexity: 10
      max_line_length: 100

# 除外パターン
exclude:
  - "tests/*"
  - "docs/*"
  - "**/migrations/*"

# カスタムルール
custom_rules:
  - id: "CUSTOM001"
    pattern: "TODO|FIXME"
    message: "未解決のTODOコメント"
    severity: "low"
```

### 環境変数

```bash
# ログレベルの設定
export SRC_CHECK_LOG_LEVEL=DEBUG

# 並列実行数の設定
export SRC_CHECK_WORKERS=4
```

## 🔗 CI/CD統合

### GitHub Actions

```yaml
name: Code Quality Check

on: [push, pull_request]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install src-check
      - run: src-check --format github
```

### pre-commitフック

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/src-check/src-check
    rev: v0.2.0
    hooks:
      - id: src-check
        args: [--fix]
```

## 📊 KPIスコアの詳細

KPIスコアは以下の4軸で評価されます：

### 機能性 (Functionality)
- テストカバレッジ
- ドキュメント充実度
- 型ヒントの完全性

### 保守性 (Maintainability)
- コードの複雑度
- 重複コード
- モジュール結合度

### 信頼性 (Reliability)
- セキュリティ問題
- エラーハンドリング
- テスト品質

### 効率性 (Efficiency)
- パフォーマンス問題
- リソース使用効率
- ビルド時間

## 🛠️ 開発

### テストの実行

```bash
# 全テストを実行
pytest

# カバレッジレポート付き
pytest --cov=src_check --cov-report=html

# 特定のテストのみ
pytest tests/checkers/test_security_checker.py
```

### コード品質チェック

```bash
# フォーマット
black src/ tests/

# リンター
ruff check src/ tests/

# 型チェック
mypy src/
```

## 📈 ロードマップ

- v0.3.0: 自動修正機能の追加
- v0.4.0: 並列処理とパフォーマンス最適化
- v1.0.0: プラグインAPI公開

## 🤝 コントリビューション

コントリビューションを歓迎します！詳細は[CONTRIBUTING.md](CONTRIBUTING.md)をご覧ください。

## 📄 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルをご覧ください。

## 🔗 リンク

- [ドキュメント](https://src-check.readthedocs.io)
- [PyPI](https://pypi.org/project/src-check)
- [GitHub](https://github.com/src-check/src-check)
- [Issue Tracker](https://github.com/src-check/src-check/issues)