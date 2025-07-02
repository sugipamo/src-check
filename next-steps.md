# src-check プロジェクト: 次のステップ

## プロジェクト現状分析

### 完了済みの作業
1. **基本構造の構築**
   - プロジェクトディレクトリ構造が整備済み
   - pyproject.tomlによるパッケージ設定完了
   - 2つのCLIエントリーポイント（src-check、src-check-kpi）実装
   - 開発ツール設定（Black、Ruff、mypy、pytest）

2. **ドキュメント整備**
   - README.md（基本的な使用方法）
   - requirements-specification.md（詳細な要件定義）

3. **初期実装**
   - CLIの引数解析とパス検証機能
   - プレースホルダーのKPIスコア表示
   - 基本的なエラーハンドリング

### 未実装の主要機能
1. **コア機能**
   - 動的モジュール探索システム
   - 実際の品質チェッカー（20+種類）
   - KPIスコアリングエンジン
   - 自動修正機能

2. **データモデル**
   - CheckResult、KPIScore、FailureLocationなどのモデル定義
   - 結果の永続化とレポート生成

3. **プロセッサー**
   - 品質ルールの実装
   - インポート管理システム
   - 自動修正エンジン

## 優先度別の次のステップ

### 優先度1: コアデータモデルの実装（1週間）
```
src_check/models/
├── __init__.py
├── check_result.py     # CheckResult, FailureLocation
├── kpi_score.py        # KPIScore, CategoryScore
└── config.py           # Configuration models
```

**実装内容:**
- CheckResult: タイトル、失敗箇所、修正ポリシー、修正例
- KPIScore: 4軸評価（コード品質、アーキテクチャ、テスト、セキュリティ）
- Config: YAML/JSON設定の読み込みと検証

### 優先度2: 基本的な品質チェッカーの実装（2週間）
```
src_check/processors/rules/
├── __init__.py
├── security/
│   ├── hardcoded_secrets/
│   │   └── main.py
│   └── dangerous_functions/
│       └── main.py
├── code_quality/
│   ├── naming_conventions/
│   │   └── main.py
│   └── print_statements/
│       └── main.py
└── architecture/
    └── circular_imports/
        └── main.py
```

**実装内容:**
- 各チェッカーは独立したmain()関数を持つ
- ASTベースの静的解析
- CheckResultを返す統一インターフェース

### 優先度3: 動的モジュール探索システム（1週間）
```
src_check/core/
├── __init__.py
├── dynamic_importer.py   # 動的インポート実行
├── module_explorer.py    # DFS探索によるmain.py発見
└── executor.py          # 安全な実行環境
```

**実装内容:**
- processors/rules/配下のmain.pyファイルをDFS探索
- 独立した名前空間での安全な実行
- 例外の適切なハンドリング

### 優先度4: KPIスコアリングエンジン（1週間）
```
src_check/core/scoring/
├── __init__.py
├── calculator.py        # スコア計算ロジック
├── aggregator.py        # 結果の集約
└── reporter.py          # レポート生成
```

**実装内容:**
- 重み付け可能な4軸評価
- 0-100点のスコア計算
- テキスト/JSON/Markdown形式のレポート

### 優先度5: 自動修正機能（2週間）
```
src_check/processors/auto_correct/
├── __init__.py
├── import_fixer.py      # インポート修正
├── code_formatter.py    # コード整形
└── cleaner.py          # 不要ファイル削除
```

**実装内容:**
- ASTを使用した安全な修正
- インポートパスの自動修正
- 空フォルダ・不要ファイルの削除

## 開発推奨事項

### 1. テスト駆動開発
- 各モジュールに対応するテストを先に作成
- pytest-covでカバレッジ80%以上を維持
- モックを活用した単体テストの充実

### 2. 段階的リリース
- v0.1.0: 基本的な品質チェック（5種類）
- v0.2.0: KPIスコアリング機能
- v0.3.0: 自動修正機能
- v1.0.0: 全機能実装

### 3. CI/CD設定
- GitHub Actionsによる自動テスト
- pre-commitフックの設定
- 自動リリースワークフロー

### 4. ドキュメント整備
- Sphinx/MkDocsによるAPI文書
- 使用例とベストプラクティス
- プラグイン開発ガイド

## 技術的考慮事項

### パフォーマンス最適化
- マルチプロセッシングによる並列実行
- キャッシュ機構の実装
- 大規模プロジェクト対応

### エラーハンドリング
- graceful degradationの実装
- 詳細なエラーメッセージ
- リカバリー機能

### 拡張性
- プラグインシステムの設計
- カスタムルールの追加サポート
- 外部ツールとの連携

## まとめ

src-checkプロジェクトは基本的な骨組みが完成しており、次は実際の機能実装フェーズに入ります。優先度に従って段階的に開発を進めることで、早期に使用可能なバージョンをリリースし、フィードバックを得ながら改善していくことが推奨されます。

特に重要なのは：
1. データモデルの適切な設計（今後の拡張性に影響）
2. テストの充実（品質保証ツールとしての信頼性）
3. パフォーマンスの考慮（実用性の確保）

これらを念頭に置きながら、アジャイルな開発プロセスで進めていくことが成功への鍵となるでしょう。