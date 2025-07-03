# PerformanceChecker

## 概要と目的

PerformanceCheckerは、Pythonコードのパフォーマンスボトルネックと非効率的なコードパターンを検出するチェッカーです。ループ内での非効率な処理、文字列連結、不要な型変換などを検出し、より高速なコードの記述を支援します。

## 検出される問題（エラーコード）

### PERF001 - ループ範囲での関数呼び出し
- `for i in range(len(func()))`のような繰り返し評価される関数呼び出し
- 重要度: MEDIUM

### PERF002 - while条件での関数呼び出し
- while条件で毎回評価される関数呼び出し
- 重要度: MEDIUM

### PERF003 - ループ内での文字列連結
- `+=`による文字列連結（非効率）
- 重要度: MEDIUM

### PERF004 - 深くネストした内包表記
- 可読性とパフォーマンスを損なう深いネスト
- 重要度: LOW

### PERF005 - 不要な型変換
- `list(list(...))`のような冗長な変換
- 重要度: LOW

### PERF006 - ループ不変な関数呼び出し
- ループ内で結果が変わらない関数呼び出し
- 重要度: MEDIUM

### PERF007 - ループ不変な計算
- ループ外に移動可能な計算
- 重要度: MEDIUM

### PERF008 - ループ内での文字列連結（+=）
- 文字列への`+=`操作
- 重要度: MEDIUM

## 設定オプション

現在、PerformanceCheckerには設定可能なオプションはありません。

## 検出される問題の例

### ループ範囲での関数呼び出し
```python
# 悪い例
for i in range(len(get_items())):  # get_items()が毎回呼ばれる可能性
    process(i)

# 良い例
items = get_items()
for i in range(len(items)):
    process(i)

# さらに良い例
for i, item in enumerate(get_items()):
    process(i, item)
```

### while条件での関数呼び出し
```python
# 悪い例
while calculate_remaining() > 0:  # 毎回計算される
    process_one()

# 良い例
remaining = calculate_remaining()
while remaining > 0:
    process_one()
    remaining = calculate_remaining()
```

### ループ内での文字列連結
```python
# 悪い例
result = ""
for item in items:
    result += str(item) + ", "  # O(n²)の複雑度

# 良い例
result_parts = []
for item in items:
    result_parts.append(str(item))
result = ", ".join(result_parts)  # O(n)の複雑度

# さらに良い例（内包表記）
result = ", ".join(str(item) for item in items)
```

### 深くネストした内包表記
```python
# 悪い例
result = [[[func(x, y, z) for z in range(10)] 
          for y in range(10)] 
         for x in range(10)]

# 良い例
result = []
for x in range(10):
    row = []
    for y in range(10):
        col = []
        for z in range(10):
            col.append(func(x, y, z))
        row.append(col)
    result.append(row)
```

### ループ不変な計算
```python
# 悪い例
for item in items:
    max_value = max(reference_list)  # 毎回同じ計算
    if item > max_value:
        process(item)

# 良い例
max_value = max(reference_list)  # ループ外で一度だけ計算
for item in items:
    if item > max_value:
        process(item)
```

## 一般的な問題の修正方法

### 1. リスト内包表記の活用
```python
# 悪い例
result = []
for x in range(100):
    if x % 2 == 0:
        result.append(x * x)

# 良い例
result = [x * x for x in range(100) if x % 2 == 0]

# ジェネレータ式（メモリ効率が良い）
result = (x * x for x in range(100) if x % 2 == 0)
```

### 2. 効率的な文字列操作
```python
# 悪い例
def build_csv(data):
    csv = ""
    for row in data:
        csv += ",".join(str(cell) for cell in row) + "\n"
    return csv

# 良い例
def build_csv(data):
    rows = []
    for row in data:
        rows.append(",".join(str(cell) for cell in row))
    return "\n".join(rows)

# さらに良い例（io.StringIO）
from io import StringIO

def build_csv(data):
    buffer = StringIO()
    for row in data:
        buffer.write(",".join(str(cell) for cell in row))
        buffer.write("\n")
    return buffer.getvalue()
```

### 3. 事前計算とキャッシュ
```python
from functools import lru_cache

# 悪い例
def process_data(items):
    for item in items:
        # 高コストな計算を毎回実行
        reference_value = expensive_calculation()
        if item > reference_value:
            yield item

# 良い例
def process_data(items):
    # 一度だけ計算
    reference_value = expensive_calculation()
    for item in items:
        if item > reference_value:
            yield item

# キャッシュを使用
@lru_cache(maxsize=128)
def expensive_calculation(param):
    # 結果をキャッシュ
    return complex_computation(param)
```

### 4. 適切なデータ構造の選択
```python
# 悪い例 - リストでの存在確認
def has_duplicates(items):
    seen = []
    for item in items:
        if item in seen:  # O(n)の操作
            return True
        seen.append(item)
    return False

# 良い例 - セットを使用
def has_duplicates(items):
    seen = set()
    for item in items:
        if item in seen:  # O(1)の操作
            return True
        seen.add(item)
    return False

# さらに良い例
def has_duplicates(items):
    return len(items) != len(set(items))
```

### 5. バルク操作の活用
```python
# 悪い例
for user_id in user_ids:
    user = db.get_user(user_id)  # N回のデータベースアクセス
    process_user(user)

# 良い例
users = db.get_users(user_ids)  # 1回のデータベースアクセス
for user in users:
    process_user(user)
```

## ベストプラクティス

1. **プロファイリング**: 推測せず、実際のボトルネックを測定
2. **アルゴリズムの選択**: O(n²)よりO(n log n)やO(n)のアルゴリズムを選択
3. **遅延評価**: ジェネレータを使用してメモリ効率を向上
4. **組み込み関数の活用**: `sum()`, `min()`, `max()`などは最適化されている
5. **NumPyの活用**: 数値計算にはNumPyのベクトル化操作を使用
6. **並列処理**: CPU集約的なタスクには`multiprocessing`、I/O集約的なタスクには`asyncio`
7. **早期終了**: 不要な処理はスキップ（`break`, `continue`, `return`）