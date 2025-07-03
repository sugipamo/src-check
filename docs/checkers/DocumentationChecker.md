# DocumentationChecker

## 概要と目的

DocumentationCheckerは、Pythonコードのドキュメントの品質と完全性を検証するチェッカーです。モジュール、クラス、関数のドキュメント文字列（docstring）の有無と品質をチェックし、コードの理解とメンテナンスを容易にします。

## 検出される問題（エラーコード）

### DOC001 - ドキュメントの欠如
- モジュールレベルのドキュメント文字列がない
- パブリッククラスのドキュメント文字列がない
- パブリック関数のドキュメント文字列がない
- 重要度: MEDIUM

### ドキュメントの不完全性
- 関数にパラメータがあるが、Args/Parametersセクションがない
- 戻り値があるが、Returns/Returnセクションがない
- 重要度: MEDIUM

## 設定オプション

現在、DocumentationCheckerには設定可能なオプションはありません。プライベートメソッド（`_`で始まる）とダンダーメソッド（`__`で囲まれる）は自動的にスキップされます。

## 検出される問題の例

### モジュールドキュメントの欠如
```python
# 悪い例 - module.py
import os
import sys

def process_data():
    pass

# 良い例 - module.py
"""データ処理モジュール

このモジュールはデータの前処理と変換機能を提供します。
"""
import os
import sys

def process_data():
    pass
```

### 関数ドキュメントの欠如
```python
# 悪い例
def calculate_total(items, tax_rate):
    return sum(item.price for item in items) * (1 + tax_rate)

# 良い例
def calculate_total(items, tax_rate):
    """アイテムの合計金額を税込みで計算する
    
    Args:
        items: 価格情報を持つアイテムのリスト
        tax_rate: 税率（0.1 = 10%）
        
    Returns:
        税込みの合計金額
    """
    return sum(item.price for item in items) * (1 + tax_rate)
```

### 不完全なドキュメント
```python
# 悪い例 - パラメータ説明がない
def send_email(recipient: str, subject: str, body: str) -> bool:
    """メールを送信する"""
    # 実装
    pass

# 良い例
def send_email(recipient: str, subject: str, body: str) -> bool:
    """指定された宛先にメールを送信する
    
    Args:
        recipient: 受信者のメールアドレス
        subject: メールの件名
        body: メール本文
        
    Returns:
        送信に成功した場合True、失敗した場合False
    """
    # 実装
    pass
```

### クラスドキュメントの欠如
```python
# 悪い例
class UserManager:
    def __init__(self):
        pass

# 良い例
class UserManager:
    """ユーザー管理を行うクラス
    
    ユーザーの作成、更新、削除、検索などの
    基本的な操作を提供します。
    """
    def __init__(self):
        pass
```

## 一般的な問題の修正方法

### 1. Google スタイルのドキュメント
```python
def complex_function(param1: str, param2: int, param3: bool = False) -> dict:
    """複雑な処理を実行する関数
    
    この関数は与えられたパラメータに基づいて複雑な処理を実行し、
    結果を辞書形式で返します。
    
    Args:
        param1: 処理対象の文字列
        param2: 処理の繰り返し回数
        param3: デバッグモードを有効にするかどうか（デフォルト: False）
        
    Returns:
        処理結果を含む辞書。以下のキーを含む：
        - 'result': 処理結果の文字列
        - 'count': 実際の処理回数
        - 'elapsed': 処理時間（秒）
        
    Raises:
        ValueError: param2が負の値の場合
        TypeError: param1が文字列でない場合
        
    Examples:
        >>> result = complex_function("test", 3)
        >>> print(result['count'])
        3
    """
    # 実装
    pass
```

### 2. NumPy スタイルのドキュメント
```python
def calculate_statistics(data: list) -> tuple:
    """データの統計情報を計算する
    
    与えられたデータリストから平均値、中央値、
    標準偏差を計算して返します。
    
    Parameters
    ----------
    data : list
        数値のリスト
        
    Returns
    -------
    tuple
        (平均値, 中央値, 標準偏差) のタプル
        
    See Also
    --------
    numpy.mean : 平均値の計算
    numpy.median : 中央値の計算
    numpy.std : 標準偏差の計算
    """
    # 実装
    pass
```

### 3. クラスのドキュメント
```python
class DataProcessor:
    """データ処理を行うクラス
    
    様々な形式のデータを読み込み、処理し、
    指定された形式で出力する機能を提供します。
    
    Attributes:
        input_format (str): 入力データの形式
        output_format (str): 出力データの形式
        encoding (str): 文字エンコーディング（デフォルト: 'utf-8'）
        
    Examples:
        >>> processor = DataProcessor('csv', 'json')
        >>> result = processor.process('data.csv')
        >>> processor.save(result, 'output.json')
    """
    
    def __init__(self, input_format: str, output_format: str):
        """DataProcessorを初期化する
        
        Args:
            input_format: 入力データの形式（'csv', 'json', 'xml'）
            output_format: 出力データの形式（'csv', 'json', 'xml'）
        """
        self.input_format = input_format
        self.output_format = output_format
        self.encoding = 'utf-8'
```

### 4. モジュールレベルのドキュメント
```python
"""ユーザー認証モジュール

このモジュールはユーザー認証に関する機能を提供します。

主な機能:
- ユーザーのログイン/ログアウト
- パスワードの検証とハッシュ化
- セッション管理
- 二要素認証のサポート

使用例:
    from auth import authenticate, create_session
    
    user = authenticate(username, password)
    if user:
        session = create_session(user)

Note:
    このモジュールはbcryptを使用してパスワードをハッシュ化します。
    
Todo:
    * OAuth2のサポートを追加
    * リフレッシュトークンの実装
"""

import bcrypt
from datetime import datetime
from typing import Optional

# 実装...
```

## ベストプラクティス

1. **すべてのパブリックAPIをドキュメント化**: エクスポートされるすべての関数、クラス、モジュールにドキュメントを追加
2. **明確で簡潔な説明**: 最初の1行で何をするかを説明
3. **パラメータと戻り値の型と説明**: 型ヒントと合わせて説明を記載
4. **使用例の提供**: 複雑な関数には`Examples`セクションを追加
5. **例外の文書化**: 発生する可能性のある例外を`Raises`セクションに記載
6. **一貫したスタイル**: プロジェクト全体で同じドキュメントスタイルを使用
7. **自動ドキュメント生成**: Sphinxなどのツールでドキュメントを自動生成