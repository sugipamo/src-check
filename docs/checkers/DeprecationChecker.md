# DeprecationChecker

## 概要と目的

DeprecationCheckerは、Pythonコードで廃止予定（deprecated）の機能の使用を検出するチェッカーです。古いAPIの使用、推奨されない書き方、将来のPythonバージョンで削除される機能などを検出し、コードの将来互換性を確保します。

## 検出される問題（エラーコード）

### DEPR001 - 廃止予定モジュール/APIの使用
- `imp` → `importlib`
- `asyncore`/`asynchat` → `asyncio`
- `collections.MutableMapping` → `collections.abc.MutableMapping`
- 重要度: MEDIUM

### DEPR003 - 古い文字列フォーマット
- `%`による文字列フォーマット → f-stringまたは`.format()`
- 重要度: INFO

### DEPR004 - 古い非同期処理パターン
- `@coroutine` → `async def`
- `asyncio.ensure_future` → `asyncio.create_task`
- 重要度: MEDIUM/INFO

### DEPR005 - typing モジュールの古い書き方（Python 3.9+）
- `typing.List` → `list`
- `typing.Dict` → `dict`
- 重要度: INFO

### DEPR006 - ワイルドカードインポート
- `from module import *` の使用
- 重要度: MEDIUM

## 設定オプション

現在、DeprecationCheckerには設定可能なオプションはありません。Pythonバージョンに応じて適切な警告が出されます。

## 検出される問題の例

### 廃止予定モジュールの使用
```python
# 悪い例
import imp  # Python 3.4で非推奨
import asyncore  # Python 3.6で非推奨

from collections import MutableMapping  # Python 3.3から移動

# 良い例
import importlib
import asyncio

from collections.abc import MutableMapping
```

### 古い文字列フォーマット
```python
# 悪い例
name = "John"
age = 30
message = "Hello, %s! You are %d years old." % (name, age)

# 良い例 - format()
message = "Hello, {}! You are {} years old.".format(name, age)

# さらに良い例 - f-string（Python 3.6+）
message = f"Hello, {name}! You are {age} years old."
```

### typing モジュールの古い書き方
```python
# 悪い例（Python 3.9+）
from typing import List, Dict, Tuple, Optional

def process_items(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}

# 良い例（Python 3.9+）
from __future__ import annotations  # 互換性のため

def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}
```

### 古い非同期処理
```python
# 悪い例
import asyncio

@asyncio.coroutine
def old_style_coroutine():
    yield from asyncio.sleep(1)
    return "done"

# タスクの作成
future = asyncio.ensure_future(old_style_coroutine())

# 良い例
async def modern_coroutine():
    await asyncio.sleep(1)
    return "done"

# タスクの作成
task = asyncio.create_task(modern_coroutine())
```

## 一般的な問題の修正方法

### 1. モジュール移行ガイド
```python
# collections の移行
# 悪い例
from collections import Iterable, Mapping, MutableSet

# 良い例
from collections.abc import Iterable, Mapping, MutableSet

# imp から importlib への移行
# 悪い例
import imp
module = imp.load_source('module_name', '/path/to/module.py')

# 良い例
import importlib.util
spec = importlib.util.spec_from_file_location('module_name', '/path/to/module.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
```

### 2. 文字列フォーマットの現代化
```python
# 段階的な移行
# レベル1: % フォーマット（非推奨）
"Name: %s, Age: %d" % (name, age)

# レベル2: format() メソッド
"Name: {}, Age: {}".format(name, age)
"Name: {name}, Age: {age}".format(name=name, age=age)

# レベル3: f-string（推奨）
f"Name: {name}, Age: {age}"
f"Name: {name!r}, Age: {age:02d}"  # 書式指定も可能
```

### 3. 型ヒントの現代化
```python
# Python 3.9+ での移行
from __future__ import annotations  # 下位互換性のため
from typing import Union, Optional

# 古い書き方
def old_function(items: List[str], 
                count: Optional[int] = None) -> Dict[str, Union[int, str]]:
    pass

# 新しい書き方
def new_function(items: list[str], 
                count: int | None = None) -> dict[str, int | str]:
    pass
```

### 4. 非同期処理の現代化
```python
# 完全な async/await への移行
import asyncio
from typing import AsyncIterator

# 古いスタイル
@asyncio.coroutine
def old_fetch_data():
    response = yield from aiohttp.get(url)
    data = yield from response.json()
    return data

# 新しいスタイル
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# 非同期イテレータ
async def async_range(n: int) -> AsyncIterator[int]:
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i
```

### 5. 警告の抑制と移行戦略
```python
import warnings

# 一時的に警告を抑制（移行期間中）
with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    # 古いコードの実行
    old_function()

# または特定の警告のみ抑制
warnings.filterwarnings("ignore", 
                       category=DeprecationWarning,
                       module="old_module")

# 自作の廃止予定マーカー
import functools
import warnings

def deprecated(reason):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated. {reason}",
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@deprecated("Use new_function() instead")
def old_function():
    pass
```

## ベストプラクティス

1. **定期的なPythonバージョンアップ**: 最新の安定版を使用
2. **段階的な移行**: 大規模プロジェクトでは段階的に新しい書き方に移行
3. **CI/CDでの警告チェック**: DeprecationWarningを検出して修正
4. **__future__ インポートの活用**: 新機能を早期に使用
5. **互換性レイヤーの作成**: 複数のPythonバージョンをサポートする場合
6. **ドキュメントの更新**: APIの変更を明確に文書化
7. **テストの充実**: 新旧両方のコードパスをテスト