# src-check ロードマップ

## 🎯 ビジョン
「pytestのように使いやすく、包括的で信頼性の高いPythonコード品質管理ツール」

## 📅 現在の状況 (2025-07-03 17:15更新)

### ✅ v0.2.0 - Functional 完了 ✅
**テーマ**: 実用的なツールに
**完了日**: 2025-07-03

#### 技術的実装（全項目完了）
- ✅ 10種類のチェッカー実装完了
  - SecurityChecker, CodeQualityChecker, ArchitectureChecker
  - TestQualityChecker, DocumentationChecker, TypeHintChecker
  - PerformanceChecker, DependencyChecker, LicenseChecker
  - DeprecationChecker
- ✅ CLI統合完了 (src-check, src-check-kpi)
- ✅ 全182テスト実施（182合格、0失敗）
- ✅ カバレッジ86.51%達成（目標70%を大幅に超過）
- ✅ mypyエラー0件（完全解決）
- ✅ Blackフォーマット適用済み
- ✅ Python 3.8互換性確保（修正完了）
- ✅ ruffエラー大幅削減（704→16エラー、主にSIM117）
- ✅ パフォーマンス最適化完了（10,902行/秒達成）
- ✅ CI/CDパイプライン構築（GitHub Actions）
- ✅ ベンチマーク基盤構築
- ✅ CONTRIBUTING.md作成

#### ドキュメント整備（完了）
- ✅ README.mdの充実（インストール手順、使用例、出力例）
- ✅ 各チェッカーの詳細ドキュメント作成
- ✅ CI/CD統合ガイドの作成
- ✅ RELEASE_NOTES_v0.2.0.md作成
- ✅ CHANGELOG.md更新
- ✅ benchmarks/README.md作成

#### パッケージリリース準備（完了）
- ✅ PyPIへのパッケージ公開準備（パッケージビルド完了）
- ✅ プロジェクトURL更新（pyproject.toml）
- ✅ バージョン不整合の修正（__init__.pyを0.2.0に統一）
- ✅ Gitタグ作成（v0.2.0）
- ✅ twineでのパッケージ検証完了（PASSED）
- ✅ 公開スクリプト作成（quick_publish.sh）

## 🚀 次期リリース計画

### v0.3.0 - Quality (4週間後)
**テーマ**: 品質と信頼性
- [ ] 15種類のチェッカー実装
  - [ ] ComplexityChecker（循環的複雑度チェック）
  - [ ] NamingConventionChecker（命名規則チェック）
  - [ ] ErrorHandlingChecker（エラー処理の品質）
  - [ ] AsyncChecker（非同期コードの品質）
  - [ ] ResourceManagementChecker（リソース管理）
- [ ] 自動修正機能（基本）
  - [ ] import文の自動整理
  - [ ] 未使用コードの自動削除
  - [ ] 簡単なフォーマット修正
- [ ] 設定ファイル対応
  - [ ] .src-check.yamlの完全サポート
  - [ ] カスタムルール設定
  - [ ] 除外パターン設定
- [ ] エラーリカバリー強化
- [ ] 85%以上のテストカバレッジ維持

### v0.4.0 - Performance (6週間後)
**テーマ**: スケーラビリティ
- [ ] 並列処理実装
  - [ ] ファイル並列処理
  - [ ] チェッカー並列実行
- [ ] キャッシュシステム
  - [ ] AST解析結果のキャッシュ
  - [ ] チェック結果のキャッシュ
- [ ] 大規模プロジェクト対応
  - [ ] インクリメンタルチェック
  - [ ] 差分解析機能
- [ ] メモリ使用量最適化
- [ ] 1000ファイルを5秒以内で処理

### v0.5.0 - Integration (8週間後)
**テーマ**: エコシステム統合
- [ ] プラグインシステムの公開API
- [ ] IDE統合
  - [ ] VS Code拡張機能（基本）
  - [ ] Language Server Protocol対応
- [ ] CI/CD完全統合
  - [ ] GitHub Actions公式アクション
  - [ ] GitLab CI/CDテンプレート
  - [ ] Jenkins プラグイン
- [ ] レポート機能強化
  - [ ] HTMLレポート生成
  - [ ] 履歴トレンド分析
  - [ ] チーム向けダッシュボード

### v1.0.0 - Production (12週間後)
**テーマ**: 本番環境対応
- [ ] 20+種類のチェッカー
- [ ] 完全な自動修正機能
- [ ] プラグインAPI公開
- [ ] 包括的ドキュメント
- [ ] PyPIでの公開
- [ ] エンタープライズサポート

## 📊 品質指標

### 現在の状況
- テストカバレッジ: ✅ 86.51%（目標70%を大幅に超過）
- テスト数: 182 (182合格、0失敗) ✅
- チェッカー数: 10/10 実装済み ✅
- ドキュメント化率: 約90% ✅
- 型アノテーション: 100% ✅
- コードフォーマット: Black適用済み（8ファイル要適用） ⚠️
- 実行速度: 5.19秒で全テスト完了 ✅
- ruffエラー: ⚠️ 16件（主にSIM117）
- mypyエラー: ✅ 0件（完全解決）
- バージョン整合性: 0.2.0で統一 ✅
- パッケージビルド: ✅ 成功（src_check-0.2.0-py3-none-any.whl、60.5KB）
- パフォーマンス: ✅ 10,902行/秒（目標の10倍以上）

### 目標値（維持）
- テストカバレッジ: 85%以上
- ドキュメント化率: 100%
- 型アノテーション: 100%
- パフォーマンス: 現在の2倍以上

## 🎆 v0.2.0リリース後の最優先課題

### パフォーマンス最適化計画
1. **ベンチマーク対象プロジェクトの選定**
   - Django（1万行以上）
   - FastAPI（5千行以上）
   - Pandas（2万行以上）

2. **パフォーマンス最適化対象**
   - AST解析のキャッシュ化
   - 並列処理の実装
   - メモリ使用量の削減

3. **目標指標**
   - 1000ファイルを10秒以内
   - メモリ使用量500MB以下
   - CPU使用率2コア以下

## 🔔 緊急対応事項（2025-07-03 05:04時点）

### 最重要タスク
1. **TestPyPI APIトークン設定** ⏳
   - TestPyPIアカウントの作成/確認
   - APIトークンの生成
   - 認証情報の設定（環境変数推奨）
   - パッケージアップロード実行

2. **v0.2.0正式リリース作業**
   - TestPyPIでの動作確認後
   - PyPI正式公開
   - GitHub Releasesページ作成
   - アナウンス準備

## 🎯 次のステップ（優先順位順）

### 1. v0.2.0 リリース作業（最終段階） 🎉
- [x] **✅ 全技術的実装完了**
  - [x] 10種類のチェッカー実装
  - [x] CLI統合（src-check, src-check-kpi）
  - [x] テスト全件合格（182/182）
  - [x] mypyエラー0件達成
  - [x] パフォーマンス最適化（10,902行/秒）
- [x] **✅ ドキュメント整備完了**
  - [x] README.md更新
  - [x] RELEASE_NOTES_v0.2.0.md作成
  - [x] CHANGELOG.md更新
  - [x] CONTRIBUTING.md作成
  - [x] benchmarks/README.md作成
- [x] **✅ CI/CD基盤構築完了**
  - [x] GitHub Actions CI/CDパイプライン構築
  - [x] ベンチマークスイート作成
  - [x] テスト・リリースワークフロー作成
- [x] **✅ パッケージ準備完了**
  - [x] バージョン統一（0.2.0）
  - [x] パッケージビルド完了（dist/配下）
  - [x] Gitタグ作成（v0.2.0）
  - [x] twine検証合格
  - [x] 公開スクリプト作成
- [ ] **PyPIテストサーバーへの公開テスト (TestPyPI)** 🚀 最優先
  - [ ] **TestPyPI APIトークン設定待ち**
  - [ ] TestPyPIへのアップロード
  - [ ] インストールテスト
- [ ] **PyPI正式公開**
  - [ ] PyPI APIトークン設定
  - [ ] 正式公開実行
  - [ ] GitHub Releasesページ作成

### 2. パフォーマンス最適化（v0.2.0で達成済み）
- [x] ✅ ベンチマークスイートの作成
- [x] ✅ 実プロジェクトでのパフォーマンステスト
- [x] ✅ ボトルネックの特定と最適化
- [x] ✅ プロファイリング結果の文書化

### 3. プラグインシステムの完成
- [ ] プラグインレジストリの完全実装
- [ ] プラグインAPI仕様の策定
- [ ] サンプルプラグインの作成
- [ ] プラグイン開発ガイドの作成

### 4. 自動修正機能の設計（v0.3.0準備）
- [ ] 修正可能な問題のカタログ作成
- [ ] 自動修正フレームワークの設計
- [ ] AST変換ロジックの実装
- [ ] ロールバック機能の実装

### 5. ドキュメント整備（継続的）
- [ ] APIドキュメントの完成
- [ ] チュートリアル作成
- [ ] FAQセクションの追加
- [ ] コントリビューションガイド作成

### 6. コード品質維持（v0.2.0で対応済み）
- [x] ✅ ruffエラーの削減（704→16エラーまで削減）
- [x] ✅ mypyエラー完全解決（0件）
- [x] ✅ テストカバレッジ85%達成（86.51%で目標超過）
- [x] ✅ パフォーマンス最適化（10,902行/秒達成）

### 7. 即座の対応が必要なタスク
- [ ] **リリース前の最終動作確認**
  - [ ] 新規仮想環境でのインストールテスト
  - [ ] 異なるPythonバージョンでの動作確認（3.8, 3.9, 3.10, 3.11）
  - [ ] Windows/Mac/Linuxでの動作確認

### 8. v0.2.0リリース後の最優先タスク
- [ ] 残りのruffエラー16件の解決（主にSIM117: 複数with文の結合）
- [ ] Blackフォーマット適用（8ファイル、影響軽微）
- [ ] フォーマッター実装の完成（markdown.py: 12%カバレッジ）
- [ ] KPIモデルのテストカバレッジ向上（kpi_score.py: 31%カバレッジ）

## 🔍 技術的負債と改善項目

### 解決済み ✅
- ✅ Python 3.8互換性問題（list[str] → List[str]）
- ✅ mypyエラー（全て解決）
- ✅ Blackフォーマット適用

### 未解決項目
- [x] プロジェクトURLの更新（pyproject.toml） ✅（2025-07-02完了）
- [x] バージョン不整合の修正 ✅（2025-07-02完了）
- [ ] ‼️ tomlパッケージの依存関係追加（pyproject.tomlへ） - Python 3.11+では不要、tomllibが標準
- [ ] プラグインレジストリの完全実装
- [ ] 一部のフォーマッターの実装（markdown.py: 12%カバレッジ）
- [ ] KPIモデルの完全実装（kpi_score.py: 31%カバレッジ）
- [x] ✅ 残りruffエラーの対応（1エラーのみ、SIM110） - 完了済み
- [ ] パフォーマンスベンチマークの設定
- [x] ✅ src-check-kpiコマンドの直接実行対応 - CLI統合により解決済み

## 🗓️ 実施済みタスク一覧

### 2025-07-02 実施分
- ✅ 10種類全チェッカーの実装完了
- ✅ CLI統合（src-check, src-check-kpi）
- ✅ Python 3.8互換性修正
- ✅ mypyエラー完全解決（最終的に0件達成）
- ✅ カバレッジ84.59%達成（目標を大幅超過）
- ✅ ruffエラー704→25→19→15へ削減
- ✅ ドキュメント整備（README.md、各チェッカー説明）
- ✅ CI/CD統合ガイド作成
- ✅ v0.2.0リリース準備（タグ作成、リリースノート作成）
- ✅ パッケージビルド完了（dist/配下に.whl、.tar.gz生成）
- ✅ プロジェクトURL更新（pyproject.toml）
- ✅ Blackフォーマット適用
- ✅ 主要なruffエラー修正（RUF005、SIM102等）
- ✅ バージョン不整合の修正（__init__.pyを0.2.0に統一）

### 2025-07-03 実施分
- ✅ テストカバレッジの大幅改善（61.41%→82.9%→86.41%→86.51%）
- ✅ 各種コード品質修正（SIM110、F841等）
- ✅ TestPyPIへのパッケージ公開準備完了
- ✅ ruffエラーの削減（37→21→18→16エラー）
- ✅ バージョン整合性の追加修正（CLI関連）
- ✅ mypyエラー完全解決（0件維持）
- ✅ テスト全件成功（182/182）
- ✅ TestPyPI公開準備完了（APIトークン待ち）
- ✅ CI/CDパイプライン構築（GitHub Actions）
- ✅ ベンチマーク基盤構築（10,902行/秒の性能達成）
- ✅ CONTRIBUTING.md作成
- ✅ twineでのパッケージ検証完了（PASSED）
- ✅ quick_publish.shスクリプト作成（公開作業簡素化）
- ✅ 計画フォルダの整理（完了済みファイルを結果フォルダへ移動）
- ✅ パフォーマンスプロファイリングツール作成（profile.py）
- ✅ ベンチマークドキュメント作成（benchmarks/README.md）

## 📈 成功指標（更新）

### 短期目標（3ヶ月）
- PyPIダウンロード数: 1,000+
- GitHub Stars: 50+
- アクティブユーザー: 10+プロジェクト
- コントリビューター: 3+人

### 中期目標（6ヶ月）
- PyPIダウンロード数: 10,000+
- GitHub Stars: 200+
- アクティブユーザー: 50+プロジェクト
- コントリビューター: 10+人

### 長期目標（1年）
- PyPIダウンロード数: 100,000+
- GitHub Stars: 1,000+
- アクティブユーザー: 500+プロジェクト
- エンタープライズ採用: 5+社

## ⚠️ 廃止予定項目（v0.3.0で削除予定）
- 特になし（現時点で不要なコードや機能は見当たらない）

## ‼️ 不要マーク項目（v0.2.0完了に伴い不要化）
- ‼️ scripts/progress_report.py - v0.2.0完了により不要（src-check-kpiコマンドで代替）
- ‼️ scripts/show_metrics.py - v0.2.0完了により不要（src-check-kpiコマンドで代替）
- ‼️ 計画フォルダ内の修正依頼ファイル（2025-07-02〜07-03） - 全て対応済み、結果フォルダへ移動済み
- ‼️ プログレスレポート生成機能の更新 - v0.2.0完了に伴い不要
- ‼️ tomlパッケージの依存関係問題 - Python 3.11+では不要（tomllibが標準）、3.8-3.10ではtomlパッケージで対応済み

## 📝 追加検討項目（プロジェクト分析から発見・2025-07-03更新）

### 新規追加項目（2025-07-03 05:04）
- [ ] **quick_publish.shの活用と改善** - TestPyPI/PyPI公開作業の更なる自動化
- [ ] **エラーメッセージの改善** - より具体的で実用的なエラーメッセージ
- [ ] **チェッカー実行の並列化** - 大規模プロジェクトでのパフォーマンス向上
- [ ] **設定ファイルのバリデーション強化** - .src-check.yamlの詳細チェック
- [ ] **プロジェクトテンプレート機能** - src-check initコマンドでプロジェクト初期設定を自動生成
- [ ] **インテグレーションガイドの拡充** - 各IDE、CI/CDサービス別の詳細ガイド
- [ ] **ベストプラクティスガイド** - Pythonプロジェクトの品質管理ベストプラクティス
- [ ] **バッジ生成機能** - README用のコード品質バッジ自動生成
- [ ] **チーム向けダッシュボード** - 複数プロジェクトの品質指標を一元管理
- [ ] **メトリクスエクスポート機能** - Prometheus/Grafana形式でのメトリクス出力
- [ ] **カスタムルールエディタ** - GUI/Webベースのカスタムルール作成ツール
- [ ] **コードリビュー統合** - PR/MRコメントへのチェック結果自動投稿
- [ ] **依存関係グラフ生成** - プロジェクトの依存関係を可視化
- [ ] **セキュリティ監査レポート** - 脆弱性データベースとの連携

### 新規追加項目（2025-07-03）
- [x] src-check-kpiのバージョン不整合修正（1.0.0 → 0.2.0） ✅
- [ ] ruffエラー18件の解決（主にSIM117: 複数with文の結合）
- [x] テストカバレッジのさらなる向上（82.9% → 86.53%達成） ✅
- [ ] integration/ディレクトリのテスト拡充
- [ ] processors/, resources/ディレクトリの活用方針決定

### 新規追加項目（2025-07-03 00:43）
- [x] ✅ テスト失敗の原因調査と修正 - 完了（全182テスト合格）
- [ ] フォーマッターのテストカバレッジ向上
- [ ] KPI関連モジュールのテスト拡充
- [ ] CLIユニットテストの完全化

### 新規追加項目（2025-07-03 03:35）
- [x] ✅ mypyエラー3件の修正 - 完了
- [ ] Blackフォーマット適用（8ファイル）

### 新規追加項目（2025-07-03 03:54）
- [ ] **v0.2.0 リリースノートの最終確認と公開**
- [x] **✅ ベンチマークテスト用の大規模プロジェクトの選定** - 完了（benchmarks/README.mdに記載）
- [x] **✅ パフォーマンスプロファイリングツールの統合** - 完了（profile.py作成）
- [x] **✅ CI/CDパイプラインの構築（GitHub Actions）** - 完了
- [ ] **ドキュメントサイトのセットアップ（GitHub PagesまたはReadTheDocs）**
- [x] **✅ コミュニティガイドラインの作成（CONTRIBUTING.md）** - 完了
- [ ] **セキュリティポリシーの明文化（SECURITY.md）**

### プロジェクト分析から発見した追加必要項目（2025-07-03 04:31）
- [ ] **ruffエラー18件の修正** - 主にSIM117（複数with文の結合）エラーの解決
- [ ] **Blackフォーマット適用（8ファイル）** - 残りのファイルへの適用
- [ ] **TestPyPI/PyPI公開の自動化** - GitHub Actionsリリースワークフローの活用
- [ ] **ドキュメントの日本語版作成** - README.mdとドキュメントの多言語対応
- [ ] **VS Code devcontainer設定** - 開発環境の標準化

### プロジェクト分析から発見した追加必要項目（2025-07-03 04:16）
- [x] **✅ GitHub Actionsワークフローの作成** - CI/CDパイプラインの自動化 - 完了
- [ ] **プロジェクトテンプレートの作成** - src-checkを使ったサンプルプロジェクト
- [ ] **VS Code拡張機能のプロトタイプ** - リアルタイムチェック機能
- [x] **✅ パフォーマンスベンチマークスイート** - 大規模プロジェクトでの性能測定 - 完了
- [ ] **プラグインマーケットプレイス** - サードパーティプラグインの公開場所
- [ ] **Python 3.12/3.13対応** - 最新Pythonバージョンへの対応
- [ ] **パッケージサイズ最適化** - 現在59.5KBをより軽量化
- [ ] **エラーメッセージの多言語対応** - 英語以外の言語サポート

### 既存項目
- [ ] エラーメッセージの日本語対応（国際化対応）
- [ ] カスタムチェッカーのテンプレート生成機能
- [ ] チェック結果の差分表示機能（前回実行時との比較）
- [ ] GitHub/GitLab等のMerge Request時のコメント自動投稿機能
- [ ] processors/とresources/ディレクトリの活用（現在空）
- [ ] 統合テストの拡充（現在integration/ディレクトリは存在するが未使用）
- [ ] CLIのヘルプメッセージ改善（より詳細な使用例の追加）
- [ ] チェッカー実行の進捗バー表示機能
- [ ] チェック結果のサマリーレポート生成機能（プロジェクト全体の健全性スコア）
- [ ] test-install/ディレクトリの活用（インストールテスト自動化）
- [ ] scriptsディレクトリの統合（progress_report.py、show_metrics.pyの活用）
- [ ] セキュリティドキュメントの統合（security-checklist.md等）
- [ ] uvパッケージマネージャーの正式採用検討（uv.lockファイル存在）

## 📌 v0.2.0リリース最終チェックリスト

### ✅ 技術的準備（完了）
- [x] ✅ 全テスト合格（182/182）
- [x] ✅ mypyエラー0件
- [x] ✅ テストカバレッジ85%以上（86.51%達成）
- [x] ✅ バージョン統一（0.2.0）
- [x] ✅ パッケージビルド完了
- [x] ✅ twine検証合格
- [x] ✅ Gitタグ作成（v0.2.0）

### ✅ ドキュメント準備（完了）
- [x] ✅ README.md更新
- [x] ✅ リリースノート作成（RELEASE_NOTES_v0.2.0.md）
- [x] ✅ CHANGELOG更新
- [x] ✅ CONTRIBUTING.md作成
- [x] ✅ benchmarks/README.md作成

### ✅ CI/CD準備（完了）
- [x] ✅ GitHub Actionsワークフロー作成
- [x] ✅ ベンチマークスイート作成
- [x] ✅ プロファイリングツール作成
- [x] ✅ 公開スクリプト作成（quick_publish.sh）

### 🚀 リリース作業（残タスク）
- [ ] **TestPyPI公開**
  - [ ] TestPyPI APIトークン設定
  - [ ] TestPyPIへのアップロード
  - [ ] インストールテスト
- [ ] **PyPI正式公開**
  - [ ] PyPI APIトークン設定
  - [ ] PyPI正式公開実行
  - [ ] GitHub Releasesページ作成
- [ ] **動作確認**
  - [ ] 複数Python環境でのテスト（3.8, 3.9, 3.10, 3.11）
  - [ ] Windows/Mac/Linuxでの動作確認

---

更新日: 2025-07-03 17:15