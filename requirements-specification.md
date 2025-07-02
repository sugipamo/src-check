# src-check: 要件定義書
## Python Code Quality Analysis and KPI Scoring System

**Version**: 1.0.0  
**Date**: 2025-01-02  
**Target**: pip配布可能な独立パッケージ  

---

## 1. プロジェクト概要

### 1.1 背景
src-checkは、競技プログラミング支援ツールの一部として開発されたコード品質チェックツールを、独立したソース品質チェックツールとして発展させるプロジェクトです。市場価値を高めるため、pip配布可能でpytestのようなコマンドライン実行を目指します。

### 1.2 目的
- Pythonプロジェクトの包括的な品質分析
- 0-100点のKPIスコアによる定量的品質評価
- 自動修正機能による品質改善支援
- CI/CD統合によるDevOps品質管理

### 1.3 プロダクトビジョン
**"pytest並みに使いやすく、包括的で信頼性の高いPythonコード品質管理ツール"**

---

## 2. 機能要件

### 2.1 コア機能

#### 2.1.1 静的品質分析システム
- **プラグイン登録制**: エントリーポイントによる安全なルール管理
- **AST解析実行**: コード実行を伴わない静的解析によるパターン検出
- **設定ベース拡張**: YAMLまたはJSONによるルール設定と有効化

#### 2.1.2 包括的品質チェック（20+種類）
**セキュリティ分析**
- ハードコードされたシークレット検出
- 危険な関数使用パターン
- SQLインジェクションリスク分析
- pickle脆弱性検出

**アーキテクチャ分析**
- 循環インポート検出
- 遅延インポート分析
- 依存関係違反検出
- クリーンアーキテクチャ評価

**コード品質分析**
- 引数処理パターン
- 命名規則チェック
- print文使用分析
- 構文エラー検出

**インフラストラクチャ分析**
- 重複検出
- 操作検証
- 副作用分析

#### 2.1.3 KPIスコアリングシステム
- **4軸評価**: コード品質・アーキテクチャ・テスト・セキュリティ（各25%）
- **0-100点評価**: 定量的品質測定
- **重み付け設定可能**: プロジェクト特性に応じたカスタマイズ
- **評価レベル**: 優秀(80+)、良好(70-79)、標準(50-69)、要改善(30-49)、危険(<30)

#### 2.1.4 自動修正機能
- **残骸クリーナー**: 空フォルダ・不要ファイル削除
- **インポート依存関係整理**: 依存関係に基づくファイル再配置
- **ローカルインポート修正**: インポートパス自動修正
- **型ヒント追加**: コード品質向上支援

#### 2.1.5 包括的インポート管理
- **3段階処理**: 事前チェック → メイン実行 → 事後チェック
- **自動修正**: 壊れたインポートの修復
- **依存関係分析**: プロジェクト構造の理解と最適化

### 2.2 入出力仕様

#### 2.2.1 入力
**コマンドライン引数**
```bash
src-check [paths...] [options]
--config/-c <file>     # 設定ファイル指定
--format <format>      # 出力形式（text/json/markdown）
--output/-o <file>     # 出力ファイル指定
--threshold <score>    # 品質閾値設定
--verbose/-v           # 詳細出力
--kpi-only            # KPI専用モード
--help/-h             # ヘルプ表示
--version             # バージョン情報
```

**設定ファイル（YAML）**
```yaml
base_score: 50.0
weights:
  code_quality: 0.25
  architecture_quality: 0.25
  test_quality: 0.25
  security_quality: 0.25
severity_impacts:
  critical: -10.0
  high: -5.0
  medium: -3.0
  low: -1.0
  info: -0.5
```

#### 2.2.2 出力
**標準出力**
```
============================================================
📊 KPIスコア評価結果
============================================================
総合スコア: 72.3/100
  - コード品質:         24.1 (15 件)
  - アーキテクチャ品質: 28.5 (3 件)
  - テスト品質:         19.7 (8 件)
  - セキュリティ品質:   19.7 (8 件)

✅ 良好: コード品質は良好なレベルです。
```

**ファイル出力**
```
.src-check-results/
├── summary.txt          # サマリーレポート
├── kpi_score.txt        # KPIスコア（テキスト）
├── kpi_score.json       # KPIスコア（JSON）
├── detailed/            # 詳細レポート
└── logs/                # 実行ログ
```

### 2.3 ユーザーワークフロー

#### 2.3.1 標準分析ワークフロー
1. **前処理**: ファイルパス検証・対象ファイル収集
2. **プラグイン読込**: 登録済みチェッカーの読み込み
3. **静的解析**: 各ファイルのAST解析とパターン検出
4. **KPI計算**: 4軸での品質スコア算出
5. **レポート生成**: 包括的レポート・サマリー作成
6. **後処理**: 結果の集約とクリーンアップ
7. **自動修正**: 検出された問題の選択的自動修正

#### 2.3.2 拡張メカニズム
**新しいルール追加**
```python
# src_check/rules/my_checker.py
from src_check.core.base import BaseChecker

class MyChecker(BaseChecker):
    def check(self, ast_tree, file_path) -> CheckResult:
        # AST解析によるパターン検出
        return CheckResult(
            title="my_checker",
            failure_locations=[...],
            fix_policy="修正方針",
            fix_example_code="修正例"
        )
```

**エントリーポイント登録**
```toml
# pyproject.toml
[project.entry-points."src_check.rules"]
my_checker = "my_package.rules:MyChecker"
```

---

## 3. 非機能要件

### 3.1 パフォーマンス要件
- **実行速度**: 中規模プロジェクト（1000ファイル未満）で5秒以内
- **メモリ使用量**: 500MB以内（大規模プロジェクト）
- **並列処理**: 設定可能なワーカー数での並列実行対応
- **キャッシュ**: モジュールキャッシュ・シンボルキャッシュによる高速化

### 3.2 信頼性要件
- **graceful degradation**: 個別チェッカー失敗時の継続実行
- **例外分離**: モジュール実行の独立性確保
- **構造化ログ**: DEBUG〜CRITICALの5段階ログレベル
- **回復機能**: インポートエラー修復・構文エラー処理

### 3.3 使いやすさ要件
- **直感的CLI**: pytest風のコマンドライン設計
- **視覚的フィードバック**: 絵文字・色分けによる結果表示
- **複数出力形式**: テキスト・JSON・Markdown対応
- **詳細ヘルプ**: コマンドライン・設定ファイルの包括的説明

### 3.4 互換性要件
- **Python版**: 3.8+ サポート
- **OS対応**: Linux・macOS・Windows対応
- **最小依存**: 標準ライブラリ中心（PyYAMLのみオプション）
- **CI/CD統合**: Jenkins・GitHub Actions・GitLab CI対応

### 3.5 セキュリティ要件
- **安全なコード解析**: ASTパーサーのみ使用（動的実行なし）
- **静的解析**: コード実行を伴わない安全な解析
- **パス検証**: ディレクトリトラバーサル防止
- **入力検証**: ファイル形式・内容の検証
- **プラグイン検証**: 登録されたプラグインの署名検証

### 3.6 保守性要件
- **モジュラー設計**: core・processors・models・utilitiesの明確分離
- **プラグインアーキテクチャ**: エントリーポイントによる安全な拡張性
- **関心の分離**: インポート修正・チェック・スコアリングの独立
- **包括的テスト**: 単体・統合・エンドツーエンドテスト

---

## 4. 技術要件

### 4.1 技術スタック
**Python環境**
- Python 3.8+ （dataclass、f-string、pathlib対応）
- 標準ライブラリ中心設計

**必須依存関係**
```python
# 標準ライブラリのみ
ast, importlib, pathlib, json, time, argparse, 
dataclasses, enum, typing, sys, os, io, subprocess, 
shutil, re
```

**オプション依存関係**
```python
pyyaml>=5.0          # YAML設定ファイル対応
pytest>=6.0          # テスティング（開発時）
```

### 4.2 アーキテクチャ要件

#### 4.2.1 パッケージ構造
```
src_check/
├── __init__.py                     # パッケージ初期化
├── cli/                            # CLI インターフェース
│   ├── main.py                     # メインCLI
│   └── kpi.py                      # KPI専用CLI
├── core/                           # コア機能
│   ├── base.py                     # 基底チェッカークラス
│   ├── registry.py                 # プラグインレジストリ
│   ├── ast_analyzer.py             # AST解析エンジン
│   ├── result_writer.py            # 結果出力
│   ├── scoring/                    # KPIスコアリング
│   └── database/                   # データ永続化
├── processors/                     # 分析プロセッサ
│   ├── rules/                      # 品質ルール
│   └── auto_correct/               # 自動修正
├── models/                         # データモデル
├── orchestrator/                   # 実行管理
├── compatibility/                  # 後方互換性
├── utils/                          # ユーティリティ
└── resources/                      # 静的リソース
```

#### 4.2.2 プラグインシステム
- **エントリーポイント**: setuptools entry_points による安全な登録
- **レジストリパターン**: プロセッサ管理
- **ファクトリパターン**: 結果生成・フォーマット
- **ストラテジパターン**: 複数実行モード
- **プラグイン検証**: インポート前の安全性確認

#### 4.2.3 設定管理
- **階層設定**: CLI引数 > プロジェクト設定 > ユーザー設定 > デフォルト
- **複数形式**: YAML・JSON・環境変数対応
- **検証機能**: 設定値の妥当性チェック

### 4.3 開発要件

#### 4.3.1 ビルドシステム
```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "src-check"
version = "1.0.0"
description = "Static code quality analysis and KPI scoring system"
requires-python = ">=3.8"
dependencies = ["pyyaml>=5.0"]

[project.entry-points."src_check.rules"]
# ビルトインルール
security = "src_check.rules.security:SecurityChecker"
architecture = "src_check.rules.architecture:ArchitectureChecker"
code_quality = "src_check.rules.code_quality:CodeQualityChecker"
test_quality = "src_check.rules.test_quality:TestQualityChecker"
```

#### 4.3.2 エントリーポイント
```python
[project.scripts]
src-check = "src_check.cli.main:main"
src-check-kpi = "src_check.cli.kpi:main"

[project.entry-points."src_check.rules"]
# 外部プラグインもここに追加可能
```

#### 4.3.3 テスト要件
- **pytest**: 単体・統合テスト
- **モック実装**: 外部依存関係のモック
- **カバレッジ**: 80%以上のテストカバレッジ
- **クロスプラットフォーム**: Linux・macOS・Windows

### 4.4 配布要件

#### 4.4.1 パッケージメタデータ
```python
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers", 
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Quality Assurance",
]
```

#### 4.4.2 リソースファイル
- `processors/` ディレクトリ（分析ルール）
- `templates/` ディレクトリ（レポートテンプレート）
- `config/` ディレクトリ（デフォルト設定）
- 静的リソース（CSS・JS）

### 4.5 実行時環境

#### 4.5.1 環境初期化
- 設定ディレクトリ作成
- データベース初期化
- ログ設定
- Python版互換性確認

#### 4.5.2 リソース管理
- プラグインの遅延読み込み
- 一時ファイル処理
- データベース接続管理
- 並列実行でのメモリ管理
- ASTキャッシュによるメモリ効率化

---

## 5. pip配布・CLI実行要件

### 5.1 インストール仕様
```bash
# 標準インストール
pip install src-check

# 開発版インストール  
pip install -e .

# オプション機能付き
pip install src-check[yaml]
```

### 5.2 CLI実行仕様
```bash
# 基本実行（pytest風）
src-check                              # カレントディレクトリ
src-check path/to/project              # 特定パス
src-check src/ tests/ utils/           # 複数パス

# 設定・出力オプション
src-check --config myconfig.yaml      # 設定ファイル指定
src-check --format json --output report.json  # 出力形式
src-check --threshold 70               # 品質閾値
src-check --verbose                    # 詳細出力

# 専用モード
src-check --kpi-only                   # KPI専用モード
src-check --help                       # ヘルプ
src-check --version                    # バージョン情報
```

### 5.3 設定ファイル検索
1. `--config` 指定ファイル
2. `./.src-check.yaml` （プロジェクト）
3. `~/.src-check.yaml` （ユーザー）
4. `/etc/src-check/config.yaml` （システム）
5. パッケージ内蔵デフォルト

### 5.4 出力ディレクトリ
```
.src-check-results/
├── summary.txt          # サマリーレポート
├── kpi_score.txt        # KPIスコア（テキスト）
├── kpi_score.json       # KPIスコア（JSON）
├── detailed/            # 詳細レポート
│   ├── code_quality.txt
│   ├── architecture.txt
│   ├── test_quality.txt
│   └── security.txt
└── logs/                # 実行ログ
    ├── execution.log
    └── operations/
```

### 5.5 終了コード仕様
- **0**: 成功
- **1**: 品質閾値未達
- **2**: 設定エラー
- **3**: システムエラー

---

## 6. 成功指標

### 6.1 定量指標
- **実行速度**: 1000ファイルプロジェクトで5秒以内
- **精度**: 既知品質問題の95%以上検出
- **安定性**: 1000回実行での99%成功率
- **互換性**: Python 3.8-3.12での動作確認

### 6.2 定性指標
- **使いやすさ**: pytest並みの直感的操作
- **信頼性**: 企業CI/CDでの実用性
- **拡張性**: 新規ルール追加の容易さ
- **保守性**: 長期メンテナンス可能な設計

### 6.3 市場指標
- **pip人気度**: 月間ダウンロード数
- **GitHub統計**: Star・Fork・Issue対応
- **コミュニティ**: 貢献者・プラグイン開発
- **企業採用**: CI/CD統合事例

---

## 7. 制約事項

### 7.1 技術制約
- Python 3.8+ 必須
- 標準ライブラリ中心（外部依存最小化）
- クロスプラットフォーム対応必須
- メモリ使用量500MB以内

### 7.2 互換性制約  
- 既存設定ファイルとの後方互換性
- 既存結果フォーマットとの互換性
- 段階的移行サポート

### 7.3 セキュリティ制約
- コード実行なし（静的AST解析のみ）
- プラグインの事前登録制による安全性確保
- 入力検証の徹底
- 機密情報の取り扱い注意
- 外部プラグインの署名検証（オプション）

---

## 8. 開発ロードマップ

### 8.1 Phase 1: Core Package (4週間)
- [ ] pyproject.toml設定
- [ ] パッケージ構造再編
- [ ] CLI実装
- [ ] 基本テスト整備

### 8.2 Phase 2: Quality Assurance (3週間)  
- [ ] クロスプラットフォームテスト
- [ ] パフォーマンス最適化
- [ ] セキュリティ監査
- [ ] ドキュメント整備

### 8.3 Phase 3: Release (2週間)
- [ ] pip配布準備
- [ ] CI/CD設定
- [ ] リリース自動化
- [ ] コミュニティ準備

### 8.4 Phase 4: Enhancement (継続)
- [ ] ユーザーフィードバック対応
- [ ] 新機能追加
- [ ] パフォーマンス改善
- [ ] エコシステム拡張

---

**この要件定義書は、現在のsrc_check実装の包括的分析に基づいて作成され、pip配布可能な高品質Pythonコード品質管理ツールの開発指針を提供します。**