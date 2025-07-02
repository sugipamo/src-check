# src-check ロードマップ

## 🎯 ビジョン
「pytestのように使いやすく、包括的で信頼性の高いPythonコード品質管理ツール」

## 📅 リリース計画

### v0.1.0 - Foundation (2週間後)
**テーマ**: 基本機能の動作確認
- ✅ コアデータモデル (BaseChecker, CheckResult, Config, KpiScore実装済み)
- ✅ 4つの基本チェッカー (security, code_quality, architecture, test_quality実装済み)
- ✅ プラグインレジストリ (PluginRegistry実装済み、discover_plugins機能付き)
- ✅ 基本的なCLI統合 (main.py, kpi.py実装済み)
- ✅ AnalysisEngine実装済み (ファイル・ディレクトリ解析機能)
- ✅ KPICalculator実装済み (スコア計算ロジック)
- ✅ ConfigLoader実装済み (YAML/JSON/pyproject.toml対応)
- ✅ 3つの出力フォーマッター実装済み (text/json/markdown)
- ⬜ 簡単な使用例

### v0.2.0 - Functional (4週間後)
**テーマ**: 実用的なツールに
- ✅ KPIスコアリング実装 (KPICalculator完成)
- ⬜ 10種類のチェッカー (現在4種類実装済み)
- ✅ 設定ファイル対応 (ConfigLoader実装済み、.src-check.yaml/json/pyproject.toml対応)
- ✅ 3つの出力形式（text/json/markdown）
- ⬜ パフォーマンス基準値

### v0.3.0 - Quality (6週間後)
**テーマ**: 品質と信頼性
- ⬜ 15種類のチェッカー (現在4種類実装済み: security, code_quality, architecture, test_quality)
- ⬜ 自動修正機能（基本）
- ⬜ CI/CD統合ガイド
- ⬜ エラーリカバリー
- ⬜ 85%テストカバレッジ

### v0.4.0 - Performance (8週間後)
**テーマ**: スケーラビリティ
- ⬜ 並列処理実装
- ⬜ キャッシュシステム
- ⬜ 大規模プロジェクト対応
- ⬜ メモリ使用量最適化
- ⬜ 1000ファイルを5秒以内

### v1.0.0 - Production (12週間後)
**テーマ**: 本番環境対応
- ⬜ 20+種類のチェッカー
- ⬜ 完全な自動修正機能
- ⬜ プラグインAPI公開
- ⬜ 包括的ドキュメント
- ⬜ PyPIでの公開

## 🔄 継続的改善項目

### 品質指標
- テストカバレッジ: 70% → 85% → 95% (現在37テスト全てパス)
- ドキュメント化率: 60% → 80% → 100%
- 型アノテーション: 50% → 80% → 100%
- パフォーマンス: ベースライン → 2x → 5x

### ユーザビリティ
- インストール時間: 30秒 → 15秒 → 10秒
- エラーメッセージ: 基本 → 詳細 → 対話的
- ヘルプシステム: 最小 → 充実 → インタラクティブ
- 設定: 手動 → 半自動 → 自動推奨

## 🚀 マイルストーン達成条件

### v0.1.0 チェックリスト
- [x] `src-check .` が動作する (main.pyでAnalysisEngine統合済み、ただし1つのテストが失敗中)
- [x] 4種類のチェッカーが問題を検出できる (テストで確認済み)
- [x] 基本的な結果表示 (3つのフォーマッター実装済み)
- [ ] README.mdの使用例が動く
- [x] pip install -e . が成功する (pyproject.toml設定済み)

### v0.2.0 チェックリスト  
- [x] KPIスコアが表示される (KPICalculator実装済み)
- [x] --format json が動作する (JsonFormatter実装済み)
- [x] .src-check.yaml が読み込まれる (ConfigLoader実装済み)
- [ ] 1000行のプロジェクトを10秒以内で処理
- [ ] 10種類のチェッカーが稼働 (現在4種類)

### v1.0.0 チェックリスト
- [ ] pip install src-check が動作
- [ ] 主要CIツールとの統合例
- [ ] プラグイン作成ドキュメント
- [ ] 5つ以上の実プロジェクトでの採用
- [ ] 月間1000+ダウンロード

## 📊 成功指標

### 技術指標
- バグ報告: < 5件/月
- PR採用率: > 80%
- ビルド成功率: > 99%
- リリースサイクル: 2週間

### コミュニティ指標
- GitHub Stars: 100 → 500 → 1000
- コントリビューター: 1 → 5 → 20
- 月間ダウンロード: 0 → 1000 → 10000
- 採用企業: 0 → 10 → 50

## 📋 不要になったタスク

### CLI統合の完成 (~~完了済み~~)
- ~~AnalysisEngineの実装~~ (完了済み)
- ~~KPICalculatorの実装~~ (完了済み)
- ~~OutputFormatterの実装~~ (完了済み)
- ~~ConfigLoaderの実装~~ (完了済み)

## 📝 即時実装が必要なタスク

### CLI統合の完成
- [x] AnalysisEngineの実装 (チェッカーを実行し結果を集約) ✅完了
- [x] KPICalculatorの実装 (KPIスコア計算ロジック) ✅完了
- [x] OutputFormatterの実装 (text/json/markdown形式の出力) ✅完了
- [x] ConfigLoaderの実装 (.src-check.yamlの読み込み) ✅完了

### プラグインシステム
- [x] PluginRegistryの基本実装 ✅完了
- [x] チェッカーの自動登録機能 ✅完了
- [x] プラグインディスカバリー機能 ✅完了

### ドキュメント整備
- [ ] README.mdに実際に動く使用例を追加
- [ ] 各チェッカーの詳細ドキュメント
- [ ] インストール手順の整備

### バグ修正と改善
- [ ] test_circular_import_detectionテストの失敗を修正 (ArchitectureChecker.checkメソッドの修正が必要)
- [ ] CLIの実際の動作確認と修正
- [ ] エラーハンドリングの改善
- [ ] コード品質問題の修正 (Black, Ruff, mypy対応)

### 追加チェッカーの実装
- [ ] DocumentationChecker (docstring品質チェック)
- [ ] PerformanceChecker (パフォーマンス問題検出)
- [ ] DependencyChecker (依存関係の健全性チェック)
- [ ] LicenseChecker (ライセンス整合性チェック)
- [ ] DeprecationChecker (廃止予定機能の使用検出)
- [ ] TypeHintChecker (型ヒントの充実度チェック)

### コード品質問題の修正 (最優先)
- [ ] test_circular_import_detectionテストの修正 (ArchitectureChecker実装)
- [ ] 型スタブのインストール (types-PyYAML, types-toml)
- [ ] Blackによるコードフォーマット (26ファイル)
- [ ] Ruffによるリンティングエラー修正 (620件、566件は自動修正可能)
- [ ] mypyの型アノテーション問題修正 (67件)
- [ ] CheckResultモデルの属性エラー修正 (line, message, rule_id等)

## 🎨 将来の可能性

### v2.0以降の機能案
- Web UI/ダッシュボード
- VS Code拡張機能
- 他言語サポート（JavaScript等）
- AIベースの修正提案
- チーム向け品質メトリクス
- SaaSバージョン

### エコシステム構築
- プラグインマーケットプレイス
- ベストプラクティス共有
- 業界別ルールセット
- 認証プログラム
- エンタープライズサポート

---

このロードマップは定期的に見直し、ユーザーフィードバックに基づいて調整します。