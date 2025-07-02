# Changelog

すべての注目すべき変更はこのファイルに記録されます。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.0.0/) に基づいており、
このプロジェクトは [Semantic Versioning](https://semver.org/spec/v2.0.0.html) に準拠しています。

## [0.2.0] - 2025-07-02

### 🎉 追加
- **10種類のチェッカー実装完了**
  - SecurityChecker: セキュリティ脆弱性の検出
  - CodeQualityChecker: コード品質の問題検出
  - ArchitectureChecker: アーキテクチャ問題の検出
  - TestQualityChecker: テスト品質の評価
  - DocumentationChecker: ドキュメント品質チェック
  - TypeHintChecker: 型ヒントの充実度チェック
  - PerformanceChecker: パフォーマンス問題検出
  - DependencyChecker: 依存関係の健全性チェック
  - LicenseChecker: ライセンス整合性チェック
  - DeprecationChecker: 廃止予定機能の使用検出

- **CLI統合**
  - `src-check`: メインコマンドの実装
  - `src-check-kpi`: KPIスコア計算専用コマンド
  - JSON形式での出力サポート
  - 詳細モードとカスタムチェッカー選択

- **プラグインシステム基盤**
  - チェッカーレジストリの実装
  - 動的チェッカーロード機能
  - カスタムチェッカーの登録インターフェース

### 🔧 改善
- **コード品質**
  - 全106テスト合格達成
  - テストカバレッジ84.13%達成（目標70%を大幅に超過）
  - mypyエラー0達成（完全な型安全性）
  - Blackフォーマット適用
  - Ruff設定の最新化

- **パフォーマンス**
  - 効率的なAST解析の実装
  - キャッシュメカニズムの導入
  - 3.10秒で全テスト完了

- **ドキュメント**
  - README.mdの大幅改善
  - 実行例と出力サンプルの追加
  - 各チェッカーの詳細説明
  - インストール手順の明確化

### 🐛 修正
- 型ヒントの不整合を修正
- 依存関係解析のパッケージ名マッピング対応（PIL→pillow等）
- ライセンス検出の精度向上
- 廃止予定機能検出パターンの拡充

### 📦 依存関係
- types-PyYAML, types-tomlを開発依存関係に追加
- Python 3.8以上のサポート継続

### 📝 その他
- プロジェクトURLの更新
- バージョン番号を0.2.0に統一
- テストデータの整理と充実

## [0.1.0] - 2025-06-15

### 🎉 追加
- 初回リリース
- 基本的なチェッカーフレームワーク
- SecurityCheckerとCodeQualityCheckerの実装
- 基本的なCLIインターフェース

[0.2.0]: https://github.com/src-check/src-check/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/src-check/src-check/releases/tag/v0.1.0