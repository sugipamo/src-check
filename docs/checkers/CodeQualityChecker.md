# CodeQualityChecker

## 概要と目的

CodeQualityCheckerは、Pythonコードの品質とベストプラクティスの遵守を検証するチェッカーです。PEP 8の命名規則、不要なprint文、複雑すぎる関数、未使用のインポートなどを検出し、保守性の高いコードの記述を支援します。

## 検出される問題（エラーコード）

### 命名規則違反
- 関数名: snake_case（例: `get_user_name`）でない場合
- クラス名: PascalCase（例: `UserAccount`）でない場合
- 定数: UPPER_SNAKE_CASE（例: `MAX_RETRY_COUNT`）でない場合
- 重要度: MEDIUM

### Print文の使用
- 本番コードでのprint文の使用（ロギングを推奨）
- 重要度: MEDIUM

### 高い複雑度
- McCabe循環的複雑度が10を超える関数
- 重要度: MEDIUM

### 未使用のインポート
- インポートされたが使用されていないモジュール
- 重要度: MEDIUM

## 設定オプション

現在、以下の設定がハードコードされています：
- `MAX_COMPLEXITY`: 10（関数の最大複雑度）

## 検出される問題の例

### 命名規則違反
```python
# 悪い例
def getUserName():  # camelCaseは非推奨
    pass

class user_account:  # クラスはPascalCaseにすべき
    pass

max_retry = 5  # 定数はUPPER_SNAKE_CASEにすべき
MAX_RETRY = 5  # 良い例
```

### Print文の使用
```python
# 悪い例
def process_data(data):
    print(f"Processing {len(data)} items")  # ロギングを使うべき
    result = []
    for item in data:
        print(f"Item: {item}")  # デバッグ出力
        result.append(transform(item))
    return result
```

### 高い複雑度
```python
# 悪い例 - 複雑度が高い
def complex_function(data, options):
    if options.get('validate'):
        if data.type == 'A':
            if data.value > 0:
                if data.category in ['X', 'Y']:
                    # ネストが深く、分岐が多い
                    pass
                elif data.category == 'Z':
                    pass
            else:
                pass
        elif data.type == 'B':
            pass
    # さらに多くの分岐...
```

### 未使用のインポート
```python
# 悪い例
import os
import sys
import json  # 使用されていない
from typing import List, Dict  # Dictは使用されていない

def read_file(path: str) -> List[str]:
    with open(path) as f:
        return f.readlines()
```

## 一般的な問題の修正方法

### 1. 命名規則の修正
```python
# 良い例
def get_user_name():  # snake_case
    pass

class UserAccount:  # PascalCase
    pass

MAX_RETRY_COUNT = 5  # UPPER_SNAKE_CASE

# 例外: AST visitor pattern
class MyVisitor(ast.NodeVisitor):
    def visit_FunctionDef(self, node):  # visit_で始まるメソッドは許可
        pass
```

### 2. ロギングの使用
```python
# 良い例
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    logger.info(f"Processing {len(data)} items")
    result = []
    for item in data:
        logger.debug(f"Item: {item}")
        result.append(transform(item))
    return result

# main関数内のprintは許可
def main():
    print("Application started")  # OK
```

### 3. 複雑度の削減
```python
# 良い例 - 関数を分割
def validate_data(data, options):
    if not options.get('validate'):
        return True
    
    validator = get_validator(data.type)
    return validator.validate(data)

def get_validator(data_type):
    validators = {
        'A': TypeAValidator(),
        'B': TypeBValidator(),
    }
    return validators.get(data_type, DefaultValidator())

class TypeAValidator:
    def validate(self, data):
        if data.value <= 0:
            return False
        return self._validate_category(data.category)
    
    def _validate_category(self, category):
        return category in ['X', 'Y', 'Z']
```

### 4. 未使用インポートの削除
```python
# 良い例
import os
import sys
from typing import List

def read_file(path: str) -> List[str]:
    # osとsysを実際に使用
    if not os.path.exists(path):
        sys.exit(1)
    
    with open(path) as f:
        return f.readlines()
```

## ベストプラクティス

1. **一貫した命名規則**: プロジェクト全体でPEP 8に従う
2. **適切なロギング**: 
   - DEBUG: 詳細な診断情報
   - INFO: 一般的な情報
   - WARNING: 警告
   - ERROR: エラー情報
3. **関数の単一責任**: 一つの関数は一つのことだけを行う
4. **早期リターン**: ネストを減らすために条件を満たさない場合は早期にreturn
5. **インポートの整理**: 
   - 標準ライブラリ
   - サードパーティライブラリ
   - ローカルインポート
   の順番で整理し、isortなどのツールを使用