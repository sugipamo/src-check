# LicenseChecker実装計画

## 📋 概要
src-checkツールの10番目のチェッカーとして、LicenseCheckerを実装します。
このチェッカーは、プロジェクトのライセンス整合性を検証し、依存関係のライセンス互換性をチェックします。

## 🎯 目標
1. プロジェクトのLICENSEファイルを検出・解析
2. 依存関係のライセンス互換性をチェック
3. ソースコードのコピーライトヘッダーを検証
4. ライセンス関連の問題を検出・報告

## 📝 実装タスク

### 1. LicenseChecker基本実装
- [ ] `src/src_check/rules/license.py` ファイルの作成
- [ ] BaseCheckerを継承したLicenseCheckerクラスの実装
- [ ] 基本的なチェックメソッドの実装

### 2. ライセンス検出機能
- [ ] LICENSEファイルの検出（LICENSE, LICENSE.txt, LICENSE.md等）
- [ ] 一般的なライセンスの識別（MIT, Apache-2.0, GPL, BSD等）
- [ ] pyproject.tomlからのライセンス情報読み取り
- [ ] setup.pyからのライセンス情報読み取り

### 3. 依存関係ライセンスチェック
- [ ] インストール済みパッケージのライセンス情報取得
- [ ] ライセンス互換性マトリックスの定義
- [ ] 互換性チェックロジックの実装
- [ ] コピーレフトライセンスの検出と警告

### 4. コピーライトヘッダー検証
- [ ] ソースファイルのヘッダー検出
- [ ] コピーライト情報の検証
- [ ] ライセンステキストの一貫性チェック
- [ ] 年度の妥当性チェック

### 5. エラーコード定義
```
LIC001: プロジェクトにLICENSEファイルが見つかりません
LIC002: 認識できないライセンス形式です
LIC003: ライセンス互換性の問題（{package}のライセンス{license}は互換性がありません）
LIC004: コピーレフトライセンスの依存関係が検出されました
LIC005: コピーライトヘッダーが見つかりません
LIC006: 古いコピーライト年度が使用されています
LIC007: ライセンス情報の不一致（pyproject.tomlとLICENSEファイル）
LIC008: 依存パッケージのライセンス情報が取得できません
```

### 6. テスト実装
- [ ] `tests/unit/test_license_checker.py` の作成
- [ ] 各種ライセンスファイルのテストケース
- [ ] 互換性チェックのテストケース
- [ ] コピーライトヘッダーのテストケース
- [ ] エッジケースのテスト

### 7. 統合作業
- [ ] CheckerRegistryへの登録
- [ ] CLI統合の確認
- [ ] ドキュメント更新

## 🔧 技術的考慮事項

### ライセンス互換性マトリックス
```python
COMPATIBILITY_MATRIX = {
    "MIT": ["MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC"],
    "Apache-2.0": ["MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause"],
    "GPL-3.0": ["GPL-3.0", "GPL-3.0+", "AGPL-3.0"],
    "GPL-2.0": ["GPL-2.0", "GPL-2.0+", "GPL-3.0", "GPL-3.0+"],
    # ... 他のライセンス
}
```

### 依存関係ライセンス取得方法
- `importlib.metadata`を使用してインストール済みパッケージの情報取得
- PyPIからの情報取得（オプション）
- requirements.txtとの照合

## 📊 成功基準
- [ ] 主要なオープンソースライセンスを識別できる
- [ ] 基本的なライセンス互換性チェックが動作する
- [ ] コピーライトヘッダーの検証が機能する
- [ ] 全テストが合格する
- [ ] カバレッジ80%以上を維持

## ⏰ 推定時間
- 基本実装: 2時間
- テスト実装: 1時間
- 統合・調整: 30分
- 合計: 約3.5時間

## 📚 参考資料
- SPDX License List: https://spdx.org/licenses/
- Choose a License: https://choosealicense.com/
- License Compatibility: https://www.gnu.org/licenses/license-compatibility.html

## 🚀 次のステップ
LicenseChecker実装完了後は、最後のチェッカーであるDeprecationCheckerの実装に進みます。