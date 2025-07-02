# src-check セキュリティチェックリスト

## ✅ 確認済み項目

### 1. 動的インポートの排除
- [x] `importlib.import_module` の使用なし
- [x] `__import__` の使用なし
- [x] `exec()` / `eval()` の使用なし
- [x] DFS探索による動的モジュール発見を静的登録に変更

### 2. 要件定義書の更新
- [x] 動的品質分析システム → 静的品質分析システム
- [x] プラグイン登録制（エントリーポイント）への移行
- [x] AST解析のみによる安全な実装
- [x] セキュリティ要件の強化

### 3. アーキテクチャの安全性
- [x] コード実行を伴わない静的解析
- [x] エントリーポイントによる明示的なプラグイン管理
- [x] サンドボックス不要（そもそも実行しない）

## ⚠️ 追加で確認が必要な項目

### 1. ファイルシステムアクセス
- [ ] パストラバーサル攻撃の防止
- [ ] シンボリックリンクの適切な処理
- [ ] 書き込み権限の最小化

### 2. 設定ファイルの検証
- [ ] YAML/JSONパーサーの安全な使用
- [ ] 設定値の適切なバリデーション
- [ ] 環境変数の安全な取り扱い

### 3. プラグインシステム
- [ ] 外部プラグインの署名検証（将来実装）
- [ ] プラグインの権限制限
- [ ] 悪意のあるプラグインの検出

### 4. リソース管理
- [ ] メモリ使用量の制限
- [ ] CPU使用率の制限
- [ ] ファイルハンドルのリーク防止

## 🔒 パッケージ配布時の推奨事項

### 1. 依存関係の管理
```toml
[project]
dependencies = [
    "pyyaml>=5.4",  # CVE-2020-14343 以降のバージョン
]
```

### 2. 最小権限の原則
- 読み取り専用のファイルアクセス（分析時）
- 書き込みは明示的に指定された出力ディレクトリのみ
- ネットワークアクセスなし

### 3. セキュリティポリシー
```python
# セキュリティポリシーの例
SECURITY_POLICY = {
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "max_ast_depth": 1000,
    "allowed_file_extensions": [".py"],
    "forbidden_paths": ["/etc", "/sys", "/proc"],
}
```

### 4. エラーハンドリング
- スタックトレースに機密情報を含めない
- ファイルパスの適切なサニタイズ
- エラーメッセージの最小化

## 📋 実装時の注意事項

### 1. AST解析の制限
```python
def safe_parse_ast(file_path: Path, max_size: int = 10_000_000):
    """安全なAST解析"""
    # ファイルサイズチェック
    if file_path.stat().st_size > max_size:
        raise ValueError("File too large")
    
    # 安全な読み込み
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read(max_size)
    
    # AST解析（実行なし）
    return ast.parse(content, filename=str(file_path))
```

### 2. パス検証
```python
def validate_path(path: Path, base_dir: Path) -> Path:
    """パスの安全性を検証"""
    resolved = path.resolve()
    base_resolved = base_dir.resolve()
    
    # パストラバーサル防止
    if not str(resolved).startswith(str(base_resolved)):
        raise ValueError("Path traversal detected")
    
    return resolved
```

### 3. プラグイン検証
```python
def validate_plugin(plugin_class):
    """プラグインの安全性を検証"""
    # BaseCheckerを継承しているか
    if not issubclass(plugin_class, BaseChecker):
        raise TypeError("Invalid plugin type")
    
    # 危険なメソッドをオーバーライドしていないか
    forbidden_methods = ['__del__', '__setattr__', '__delattr__']
    for method in forbidden_methods:
        if method in plugin_class.__dict__:
            raise SecurityError(f"Plugin overrides forbidden method: {method}")
```

## ✅ 結論

現在の要件定義書とセキュリティ移行計画により、以下が達成されています：

1. **動的インポートの完全排除** - 静的解析のみ
2. **安全なプラグインシステム** - エントリーポイント制
3. **予測可能な動作** - 明示的に登録されたチェッカーのみ
4. **監査可能性** - 全ての動作が追跡可能

これにより、pipパッケージとして安全に配布できる設計となっています。