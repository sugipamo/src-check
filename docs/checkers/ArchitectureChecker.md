# ArchitectureChecker

## 概要と目的

ArchitectureCheckerは、ソフトウェアアーキテクチャの問題とデザインの欠陥を検出するチェッカーです。循環参照、レイヤー違反、高い結合度、ゴッドクラスなどのアーキテクチャ上の問題を発見し、保守性と拡張性の高いコード構造の維持を支援します。

## 検出される問題（エラーコード）

### 循環インポート（Circular Import）
- 関数やクラス内でのインポート（循環依存の回避策の可能性）
- 重要度: HIGH

### レイヤー違反（Layer Violation）
- レイヤードアーキテクチャの違反
  - データ層 → ビジネス層/UI層への参照
  - ビジネス層 → UI層への参照
- 重要度: MEDIUM

### 高い結合度（High Coupling）
- モジュールあたりのインポート数が10を超える
- 外部呼び出しが15を超える
- 重要度: MEDIUM

### ゴッドクラス（God Class）
- メソッド数が20を超える
- 属性数が15を超える
- 行数が300を超える
- 重要度: MEDIUM

## 設定オプション

現在、以下の設定がハードコードされています：
- `MAX_IMPORTS_PER_MODULE`: 10
- `MAX_EXTERNAL_CALLS`: 15
- `MAX_METHODS`: 20
- `MAX_ATTRIBUTES`: 15
- `MAX_LINES`: 300

## 検出される問題の例

### 循環インポート
```python
# 悪い例 - module_a.py
from module_b import ClassB

class ClassA:
    def method(self):
        return ClassB()

# 悪い例 - module_b.py
def some_function():
    # 関数内でのインポート（循環依存の兆候）
    from module_a import ClassA
    return ClassA()
```

### レイヤー違反
```python
# 悪い例 - data/repository.py（データ層）
from business.service import UserService  # データ層からビジネス層への参照
from ui.controller import UserController  # データ層からUI層への参照

class UserRepository:
    def save(self, user):
        # データ層がビジネスロジックを知っている
        service = UserService()
        service.validate(user)
```

### 高い結合度
```python
# 悪い例 - 多すぎるインポート
import os
import sys
import json
import logging
import datetime
import requests
import pandas
import numpy
import matplotlib
import seaborn
import sklearn
import tensorflow
# ... さらに多くのインポート

class DataProcessor:
    # 多くの外部モジュールに依存
    pass
```

### ゴッドクラス
```python
# 悪い例 - 責任が多すぎるクラス
class UserManager:
    def __init__(self):
        self.db_connection = None
        self.cache = None
        self.logger = None
        self.validator = None
        self.email_service = None
        # ... 15以上の属性
    
    def create_user(self): pass
    def update_user(self): pass
    def delete_user(self): pass
    def authenticate_user(self): pass
    def authorize_user(self): pass
    def validate_email(self): pass
    def send_email(self): pass
    def log_activity(self): pass
    def cache_user(self): pass
    def clear_cache(self): pass
    # ... 20以上のメソッド
```

## 一般的な問題の修正方法

### 1. 循環インポートの解決
```python
# 良い例 - インターフェースの導入
# interfaces.py
from abc import ABC, abstractmethod

class IUserService(ABC):
    @abstractmethod
    def process_user(self, user_id: int): pass

# module_a.py
from interfaces import IUserService

class ModuleA:
    def __init__(self, user_service: IUserService):
        self.user_service = user_service

# module_b.py
from interfaces import IUserService

class UserService(IUserService):
    def process_user(self, user_id: int):
        # 実装
        pass
```

### 2. レイヤーアーキテクチャの遵守
```python
# 良い例 - 適切な依存関係
# data/repository.py（データ層）
class UserRepository:
    def save(self, user):
        # データの永続化のみ
        self.db.insert(user)
    
    def find_by_id(self, user_id):
        return self.db.query(user_id)

# business/service.py（ビジネス層）
from data.repository import UserRepository

class UserService:
    def __init__(self):
        self.repository = UserRepository()
    
    def create_user(self, user_data):
        # ビジネスロジック
        user = self.validate(user_data)
        return self.repository.save(user)

# ui/controller.py（UI層）
from business.service import UserService

class UserController:
    def __init__(self):
        self.service = UserService()
    
    def handle_create(self, request):
        user = self.service.create_user(request.data)
        return response(user)
```

### 3. 結合度の削減
```python
# 良い例 - 必要なものだけインポート
from typing import List, Dict
import logging

from .interfaces import DataProcessor
from .utils import validate_data

class SimpleProcessor(DataProcessor):
    """必要最小限の依存関係"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def process(self, data: List[Dict]) -> List[Dict]:
        validated = validate_data(data)
        return self._transform(validated)
```

### 4. クラスの責任分割
```python
# 良い例 - 単一責任の原則
class User:
    """ユーザーエンティティ"""
    def __init__(self, id, email, name):
        self.id = id
        self.email = email
        self.name = name

class UserRepository:
    """データアクセス"""
    def save(self, user: User): pass
    def find_by_id(self, id: int): pass
    def delete(self, id: int): pass

class UserValidator:
    """検証ロジック"""
    def validate_email(self, email: str): pass
    def validate_password(self, password: str): pass

class UserService:
    """ビジネスロジック"""
    def __init__(self, repo: UserRepository, validator: UserValidator):
        self.repo = repo
        self.validator = validator
    
    def create_user(self, data: dict): pass

class EmailService:
    """メール送信"""
    def send_welcome_email(self, user: User): pass
```

## ベストプラクティス

1. **依存性注入（DI）**: インターフェースを通じて依存関係を注入
2. **レイヤードアーキテクチャ**: 
   - プレゼンテーション層 → アプリケーション層 → ドメイン層 → インフラ層
   - 上位層は下位層のみに依存
3. **モジュール分割**: 機能ごとに適切にモジュールを分割
4. **SOLID原則**: 
   - 単一責任の原則（SRP）
   - オープン・クローズドの原則（OCP）
   - リスコフの置換原則（LSP）
   - インターフェース分離の原則（ISP）
   - 依存性逆転の原則（DIP）
5. **定期的なリファクタリング**: 技術的負債の蓄積を防ぐ