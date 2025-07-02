# PerformanceChecker実装計画

## 概要
Pythonコードのパフォーマンス問題を検出するPerformanceCheckerを実装する。

## 目的
- パフォーマンスボトルネックの早期発見
- 非効率なコードパターンの検出
- 最適化の提案

## 実装内容

### 1. 検出対象のパフォーマンス問題

#### 1.1 ループ内での重複計算
```python
# 悪い例
for i in range(1000):
    result = len(large_list) * complex_calculation()  # 毎回同じ計算
    
# 良い例
list_length = len(large_list)
calc_result = complex_calculation()
for i in range(1000):
    result = list_length * calc_result
```

#### 1.2 文字列結合の非効率性
```python
# 悪い例
result = ""
for item in items:
    result += str(item)  # O(n²)の複雑度
    
# 良い例
result = "".join(str(item) for item in items)  # O(n)
```

#### 1.3 リスト内包表記 vs ループ
```python
# 遅い
result = []
for i in range(1000):
    if i % 2 == 0:
        result.append(i * 2)
        
# 速い
result = [i * 2 for i in range(1000) if i % 2 == 0]
```

#### 1.4 不要な型変換
```python
# 悪い例
data = list(set(list(items)))  # 不要な変換
    
# 良い例
data = list(set(items))
```

#### 1.5 グローバル変数アクセス
```python
# 遅い
global_var = 100
def func():
    for i in range(1000):
        x = global_var * i  # グローバル変数の参照は遅い
        
# 速い
def func():
    local_var = global_var  # ローカル変数にコピー
    for i in range(1000):
        x = local_var * i
```

### 2. 実装するチェック機能

1. **ループ最適化チェック**
   - ループ内での不変式の検出
   - ネストループの効率性評価
   - range()の使い方チェック

2. **データ構造の選択チェック**
   - リスト vs セット vs 辞書の適切な使用
   - dequeの使用提案（頻繁な先頭要素の追加/削除）
   - defaultdictの使用提案

3. **文字列操作チェック**
   - 文字列結合の効率性
   - f-stringの使用推奨
   - 正規表現のコンパイル最適化

4. **関数呼び出しチェック**
   - 頻繁な属性アクセスの最適化
   - ラムダ vs 関数定義の適切な使用
   - 組み込み関数の活用提案

5. **メモリ効率チェック**
   - ジェネレータの使用提案
   - 大きなリストのコピー検出
   - 不要な中間変数の検出

### 3. 実装タスク

1. **PerformanceCheckerクラスの作成**
   - BaseCheckerを継承
   - ASTノードの走査メソッド実装

2. **各種パフォーマンス問題の検出ロジック**
   - visit_For: ループ最適化のチェック
   - visit_BinOp: 文字列結合のチェック
   - visit_ListComp: リスト内包表記の推奨
   - visit_Call: 関数呼び出しの最適化チェック

3. **テストケースの作成**
   - 各パフォーマンス問題のテストケース
   - 修正提案の妥当性確認
   - ベンチマークテスト

4. **ドキュメントの作成**
   - 検出可能なパフォーマンス問題の一覧
   - 各問題の改善方法
   - パフォーマンス改善の目安

### 4. 成功基準

- 10種類以上のパフォーマンス問題を検出可能
- 誤検出率5%以下
- 各問題に対する具体的な改善提案
- テストカバレッジ90%以上

### 5. スケジュール

1. Day 1: 基本クラス実装とループ最適化チェック
2. Day 2: データ構造と文字列操作チェック
3. Day 3: 関数呼び出しとメモリ効率チェック
4. Day 4: テストケース作成とドキュメント整備

## 次のステップ
1. src/src_check/rules/performance.py の作成
2. 基本的なループ最適化チェックの実装
3. テストケースの作成開始