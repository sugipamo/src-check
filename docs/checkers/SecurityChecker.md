# SecurityChecker

## 概要と目的

SecurityCheckerは、Pythonコードにおけるセキュリティ脆弱性と悪いプラクティスを検出するチェッカーです。ハードコードされた秘密情報、危険な関数の使用、SQLインジェクションの可能性、pickleモジュールの不適切な使用などを検出します。

## 検出される問題（エラーコード）

### ハードコードされた秘密情報
- パスワード、APIキー、トークンなどの機密情報がコードに直接記述されている場合に検出
- 重要度: CRITICAL

### 危険な関数の使用
- `eval()`, `exec()`, `compile()` - 任意のコードを実行可能
- `__import__()` - 動的インポートの危険性
- `subprocess` with `shell=True` - シェルインジェクションの危険性
- 重要度: HIGH

### SQLインジェクションの可能性
- SQL文の文字列連結や`format()`での組み立て
- 重要度: MEDIUM

### Pickleモジュールの使用
- 信頼できないデータのデシリアライズによる任意コード実行の危険性
- 重要度: CRITICAL

## 設定オプション

現在、SecurityCheckerには設定可能なオプションはありません。すべてのセキュリティチェックが自動的に実行されます。

## 検出される問題の例

### ハードコードされた秘密情報
```python
# 悪い例
password = "admin123"
api_key = "sk-1234567890abcdef"
SECRET_TOKEN = "my-secret-token"

config = {
    "password": "hardcoded_password",
    "api_key": "12345"
}
```

### 危険な関数の使用
```python
# 悪い例
user_input = input("Enter code: ")
eval(user_input)  # 任意のコードが実行可能

command = "ls " + user_input
os.system(command)  # コマンドインジェクション

subprocess.call(command, shell=True)  # シェルインジェクション
```

### SQLインジェクション
```python
# 悪い例
user_id = request.get("user_id")
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)

query = "SELECT * FROM users WHERE name = '%s'" % username
```

### Pickleの不適切な使用
```python
# 悪い例
import pickle

data = receive_data_from_network()
obj = pickle.loads(data)  # 信頼できないデータのデシリアライズ
```

## 一般的な問題の修正方法

### 1. 秘密情報の管理
```python
# 良い例
import os
from dotenv import load_dotenv

load_dotenv()

password = os.environ.get("DB_PASSWORD")
api_key = os.environ.get("API_KEY")

# または設定ファイルから読み込む（.gitignoreに追加）
import json
with open("secrets.json") as f:
    secrets = json.load(f)
    api_key = secrets["api_key"]
```

### 2. 安全な関数の使用
```python
# 良い例
# evalの代わりにast.literal_evalを使用
import ast
user_input = input("Enter data: ")
try:
    data = ast.literal_eval(user_input)
except (ValueError, SyntaxError):
    print("Invalid input")

# subprocessはshell=Falseで使用
import subprocess
subprocess.run(["ls", "-la"], shell=False)
```

### 3. SQLインジェクション対策
```python
# 良い例 - パラメータ化クエリ
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
cursor.execute("SELECT * FROM users WHERE name = %s", (username,))

# ORMの使用
from sqlalchemy import text
query = text("SELECT * FROM users WHERE id = :user_id")
result = connection.execute(query, user_id=user_id)
```

### 4. Pickleの代替
```python
# 良い例 - JSONを使用
import json

# シリアライズ
data = {"key": "value"}
json_str = json.dumps(data)

# デシリアライズ
obj = json.loads(json_str)

# 複雑なオブジェクトの場合はmsgpackやprotobufを検討
```

## ベストプラクティス

1. **環境変数の使用**: 秘密情報は環境変数や安全な保管庫（Vault、AWS Secrets Manager等）で管理
2. **入力検証**: すべての外部入力を検証・サニタイズ
3. **最小権限の原則**: 必要最小限の権限で実行
4. **セキュリティライブラリの活用**: 暗号化にはcryptographyなどの実績あるライブラリを使用
5. **定期的な依存関係の更新**: セキュリティパッチを含む最新版を使用