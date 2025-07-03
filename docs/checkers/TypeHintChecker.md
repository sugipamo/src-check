# TypeHintChecker

## 概要と目的

TypeHintCheckerは、Pythonコードの型ヒントの品質と完全性を検証するチェッカーです。関数のパラメータと戻り値の型ヒント、ジェネリック型の適切な使用をチェックし、型安全性の向上とIDEのサポートを最大化します。

## 検出される問題（エラーコード）

### TYPE001 - 型ヒントの欠如
- 関数パラメータに型ヒントがない
- 関数の戻り値に型ヒントがない（`__init__`は除く）
- ジェネリック型が型パラメータなしで使用されている
- 重要度: MEDIUM

## 設定オプション

現在、TypeHintCheckerには設定可能なオプションはありません。プライベートメソッド（`_`で始まる、ただし`__init__`は除く）は自動的にスキップされます。

## 検出される問題の例

### パラメータの型ヒント欠如
```python
# 悪い例
def calculate_average(numbers, precision):
    if not numbers:
        return 0
    return round(sum(numbers) / len(numbers), precision)

# 良い例
def calculate_average(numbers: list[float], precision: int) -> float:
    if not numbers:
        return 0.0
    return round(sum(numbers) / len(numbers), precision)
```

### 戻り値の型ヒント欠如
```python
# 悪い例
def get_user_by_id(user_id: int):
    # データベースからユーザーを取得
    return database.query(user_id)

# 良い例
from typing import Optional
from models import User

def get_user_by_id(user_id: int) -> Optional[User]:
    # データベースからユーザーを取得
    return database.query(user_id)
```

### ジェネリック型の不適切な使用
```python
# 悪い例
def process_items(items: list) -> dict:
    results = {}
    for item in items:
        results[item.id] = item.process()
    return results

# 良い例
from typing import Dict, List
from models import Item, ProcessResult

def process_items(items: List[Item]) -> Dict[int, ProcessResult]:
    results: Dict[int, ProcessResult] = {}
    for item in items:
        results[item.id] = item.process()
    return results
```

## 一般的な問題の修正方法

### 1. 基本的な型ヒントの追加
```python
# 良い例 - 基本型
def greet(name: str, times: int = 1) -> str:
    return f"Hello, {name}! " * times

def calculate_area(width: float, height: float) -> float:
    return width * height

def is_valid(value: str) -> bool:
    return len(value) > 0
```

### 2. コレクション型の型ヒント
```python
from typing import List, Dict, Set, Tuple, Optional

# 良い例 - コレクション型
def process_names(names: List[str]) -> List[str]:
    return [name.upper() for name in names]

def count_words(text: str) -> Dict[str, int]:
    words = text.split()
    return {word: words.count(word) for word in set(words)}

def get_unique_items(items: List[int]) -> Set[int]:
    return set(items)

def parse_coordinate(coord_str: str) -> Tuple[float, float]:
    x, y = coord_str.split(',')
    return float(x), float(y)
```

### 3. Optional と Union の使用
```python
from typing import Optional, Union

# 良い例 - Optional（None可能な値）
def find_user(user_id: int) -> Optional[User]:
    user = database.get(user_id)
    return user if user else None

# 良い例 - Union（複数の型）
def parse_number(value: Union[str, int, float]) -> float:
    if isinstance(value, str):
        return float(value)
    return float(value)
```

### 4. カスタムクラスと型エイリアス
```python
from typing import List, Dict, TypeAlias, NewType

# 型エイリアス
UserId = NewType('UserId', int)
UserData: TypeAlias = Dict[str, Union[str, int, bool]]

class User:
    def __init__(self, id: UserId, data: UserData) -> None:
        self.id = id
        self.data = data

def get_users() -> List[User]:
    # ユーザーリストを返す
    pass

def create_user(data: UserData) -> User:
    user_id = UserId(generate_id())
    return User(user_id, data)
```

### 5. ジェネリックとプロトコル
```python
from typing import Generic, TypeVar, Protocol

T = TypeVar('T')

class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
    
    def get(self) -> T:
        return self.value

# プロトコル（構造的部分型）
class Drawable(Protocol):
    def draw(self) -> None: ...

def render_all(items: List[Drawable]) -> None:
    for item in items:
        item.draw()
```

### 6. 関数型とコールバック
```python
from typing import Callable, Awaitable

# 関数型
Handler = Callable[[str, int], bool]

def register_handler(handler: Handler) -> None:
    # ハンドラーを登録
    pass

# 非同期関数
async def fetch_data(url: str) -> Dict[str, Any]:
    # データを取得
    pass

AsyncHandler = Callable[[str], Awaitable[Dict[str, Any]]]
```

## ベストプラクティス

1. **すべてのパブリック関数に型ヒントを追加**: 外部から呼ばれる可能性のある関数は必ず型ヒントを付ける
2. **具体的な型を使用**: `Any`の使用は最小限に抑える
3. **Optional を明示的に使用**: None を返す可能性がある場合は`Optional`を使用
4. **型エイリアスの活用**: 複雑な型は型エイリアスで簡潔に
5. **mypyなどの型チェッカーを使用**: 静的型チェックでエラーを早期発見
6. **段階的な型付け**: 既存のコードには徐々に型ヒントを追加
7. **ドキュメントとの一貫性**: 型ヒントとドキュメントの情報を一致させる