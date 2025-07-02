# src-check ロードマップ

## 🎯 ビジョン
「pytestのように使いやすく、包括的で信頼性の高いPythonコード品質管理ツール」

## 📅 現在の状況

### ✅ v0.1.0 - Foundation 完了
- 基本機能の実装完了
- ✅ 6つのチェッカー実装済み (security, code_quality, architecture, test_quality, documentation, type_hints)
- ✅ CLI統合完了 (src-check, src-check-kpi コマンド)
- ✅ 全55テスト合格、カバレッジ82.74%達成
- ✅ プラグインシステム基盤完成

## 🚀 次期リリース計画

### v0.2.0 - Functional (2週間後)
**テーマ**: 実用的なツールに

#### コード品質の最終調整
- [x] Blackフォーマットの適用 (4ファイル: type_hints.py, documentation.py, test_type_hint_checker.py, test_documentation_checker.py) ✅
- [x] pyproject.tomlのRuff設定更新 (lintセクションへ移行済み) ✅
- [x] 型スタブのインストール (types-PyYAML, types-toml) ✅
- [x] mypyエラーの修正 (33エラー、9ファイル) ✅

#### 追加チェッカーの実装 (10種類に拡張)
- [x] DocumentationChecker (docstring品質チェック) ✅
- [x] PerformanceChecker (パフォーマンス問題検出) ✅
- [ ] DependencyChecker (依存関係の健全性チェック)
- [ ] LicenseChecker (ライセンス整合性チェック)
- [ ] DeprecationChecker (廃止予定機能の使用検出)
- [x] TypeHintChecker (型ヒントの充実度チェック) ✅

#### ドキュメント整備
- [ ] README.mdに実際に動く使用例を追加
- [ ] 各チェッカーの詳細ドキュメント
- [ ] CI/CD統合ガイドの作成

#### パフォーマンス最適化
- [ ] 1000行のプロジェクトを10秒以内で処理
- [ ] パフォーマンス基準値の設定

### v0.3.0 - Quality (4週間後)
**テーマ**: 品質と信頼性
- [ ] 15種類のチェッカー実装
- [ ] 自動修正機能（基本）
  - [ ] import文の自動整理
  - [ ] 未使用コードの自動削除
  - [ ] 簡単なフォーマット修正
- [ ] エラーリカバリー強化
- [ ] 85%以上のテストカバレッジ維持

### v0.4.0 - Performance (6週間後)
**テーマ**: スケーラビリティ
- [ ] 並列処理実装
- [ ] キャッシュシステム
- [ ] 大規模プロジェクト対応
- [ ] メモリ使用量最適化
- [ ] 1000ファイルを5秒以内で処理

### v1.0.0 - Production (10週間後)
**テーマ**: 本番環境対応
- [ ] 20+種類のチェッカー
- [ ] 完全な自動修正機能
- [ ] プラグインAPI公開
- [ ] 包括的ドキュメント
- [ ] PyPIでの公開

## 📊 品質指標

### 現在の状況
- テストカバレッジ: 83.07% ✅
- テスト数: 66 (全て合格) ✅
- チェッカー数: 7/10 実装済み
- ドキュメント化率: 約60%
- 型アノテーション: 100% ✅ (mypyエラー0)

### 目標値
- テストカバレッジ: 85%以上を維持
- ドキュメント化率: 100%
- 型アノテーション: 100%
- パフォーマンス: 現在の2倍以上

## 🔍 現在の課題と対応

### ~~mypyエラー詳細 (33エラー)~~ ✅ 解決済み
- ~~**型アノテーションの欠落**: 関数引数、戻り値、変数の型指定~~
- ~~**互換性エラー**: AsyncFunctionDefをFunctionDefとして扱う問題~~
- ~~**属性エラー**: objectに存在しない属性へのアクセス~~
- ~~**到達不可能なコード**: 条件分岐後のコード~~
- ~~**Optionalの演算エラー**: Noneとintの減算~~

## 🔥 即時対応タスク

### ~~1. コード品質問題の修正~~ ✅ 完了
```bash
# mypyエラーの確認 ✅ エラー0
python -m mypy src/

# Blackフォーマット (4ファイル) ✅ 適用済み
python -m black src/src_check/rules/type_hints.py src/src_check/rules/documentation.py
python -m black tests/unit/test_type_hint_checker.py tests/unit/test_documentation_checker.py

# 型スタブインストール ✅ インストール済み
pip install types-PyYAML types-toml
```

### 2. 次期チェッカー実装優先順位
1. PerformanceChecker - パフォーマンス問題の早期発見
2. DependencyChecker - 依存関係の健全性確保
3. DeprecationChecker - 廃止予定機能の使用検出
4. LicenseChecker - ライセンス整合性の確認

## 📈 成功指標

### 技術指標
- バグ報告: < 5件/月
- ビルド成功率: > 99%
- リリースサイクル: 2週間

### コミュニティ指標
- GitHub Stars: 0 → 100 → 500
- 月間ダウンロード: 0 → 1000 → 10000
- 採用プロジェクト: 0 → 10 → 50

## 🎨 将来の展望

### v2.0以降
- Web UI/ダッシュボード
- VS Code拡張機能
- 他言語サポート（JavaScript等）
- AIベースの修正提案
- チーム向け品質メトリクス

### エコシステム構築
- プラグインマーケットプレイス
- ベストプラクティス共有
- 業界別ルールセット
- エンタープライズサポート

## 📝 直近の実装タスク

### 実装済みチェッカー (7種類)
1. ✅ SecurityChecker - セキュリティ脆弱性の検出
2. ✅ CodeQualityChecker - コード品質の問題検出
3. ✅ ArchitectureChecker - アーキテクチャ問題の検出
4. ✅ TestQualityChecker - テスト品質の評価
5. ✅ DocumentationChecker - ドキュメント品質チェック
6. ✅ TypeHintChecker - 型ヒントの充実度チェック
7. ✅ PerformanceChecker - パフォーマンス問題検出

### 未実装チェッカー (3種類) - v0.2.0で実装予定
1. ⏳ DependencyChecker - 依存関係の健全性チェック
2. ⏳ LicenseChecker - ライセンス整合性チェック
3. ⏳ DeprecationChecker - 廃止予定機能の使用検出

### CLI統合状況
- ✅ src-check: メインコマンド実装完了
- ✅ src-check-kpi: KPIスコア計算コマンド実装完了
- ✅ 全66テスト合格、カバレッジ83.07%達成

### PerformanceChecker実装詳細
- ✅ ループ内での不変式検出
- ✅ 文字列結合の非効率性検出
- ✅ 不要な型変換の検出
- ✅ ループ不変な関数呼び出しの検出
- ✅ 深くネストされた内包表記の検出
- ✅ 13種類のテストケース実装
- ✅ 8種類のパフォーマンス問題パターン検出 (PERF001-PERF008)

---

更新日: 2025-07-02 17:10