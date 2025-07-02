# DependencyChecker

## 概要と目的

DependencyCheckerは、Pythonプロジェクトの依存関係の健全性とセキュリティ問題を検出するチェッカーです。循環依存、未使用の依存関係、バージョンの固定されていない依存関係、開発用と本番用の依存関係の混在などを検出します。

## 検出される問題（エラーコード）

### DEP001 - 循環依存
- モジュール間の循環参照
- 重要度: HIGH

### DEP002 - 未使用の依存関係
- requirements.txtやpyproject.tomlに記載されているが使用されていないパッケージ
- 重要度: MEDIUM

### DEP006 - 固定されていないバージョン
- バージョンが指定されていない、または曖昧な指定
- 重要度: MEDIUM

### DEP007 - 開発用依存関係の混在
- pytest、flake8などの開発用ツールが本番の依存関係に含まれている
- 重要度: MEDIUM

## 設定オプション

現在、DependencyCheckerには設定可能なオプションはありません。プロジェクトレベルでの実行が必要です。

## 検出される問題の例

### 循環依存
```python
# module_a.py
from module_b import ClassB

class ClassA:
    def use_b(self):
        return ClassB()

# module_b.py
from module_a import ClassA  # 循環依存！

class ClassB:
    def use_a(self):
        return ClassA()
```

### 未使用の依存関係
```txt
# requirements.txt
requests==2.28.0
pandas==1.5.0      # コードで使用されていない
numpy==1.23.0
flask==2.2.0       # コードで使用されていない
```

### 固定されていないバージョン
```txt
# 悪い例 - requirements.txt
requests
pandas>=1.0
numpy
flask*

# 良い例 - requirements.txt
requests==2.28.0
pandas>=1.5.0,<2.0.0
numpy==1.23.0
flask==2.2.0
```

### 開発用依存関係の混在
```txt
# 悪い例 - requirements.txt（本番用）
django==4.1.0
psycopg2==2.9.0
pytest==7.2.0      # 開発用ツール
black==22.10.0     # 開発用ツール
flake8==5.0.0      # 開発用ツール

# 良い例 - requirements.txt（本番用）
django==4.1.0
psycopg2==2.9.0

# 良い例 - requirements-dev.txt（開発用）
pytest==7.2.0
black==22.10.0
flake8==5.0.0
```

## 一般的な問題の修正方法

### 1. 循環依存の解決
```python
# 解決方法1: インターフェースの導入
# interfaces.py
from abc import ABC, abstractmethod

class InterfaceA(ABC):
    @abstractmethod
    def method_a(self): pass

class InterfaceB(ABC):
    @abstractmethod
    def method_b(self): pass

# module_a.py
from interfaces import InterfaceA, InterfaceB

class ClassA(InterfaceA):
    def __init__(self, b: InterfaceB):
        self.b = b
    
    def method_a(self):
        return self.b.method_b()

# 解決方法2: 遅延インポート
# module_a.py
class ClassA:
    def use_b(self):
        from module_b import ClassB  # 使用時にインポート
        return ClassB()
```

### 2. 依存関係の整理
```toml
# pyproject.toml - 現代的な依存関係管理
[project]
name = "myproject"
dependencies = [
    "django>=4.1.0,<5.0.0",
    "psycopg2-binary>=2.9.0,<3.0.0",
    "redis>=4.0.0,<5.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.2.0",
    "pytest-cov>=4.0.0",
    "black>=22.10.0",
    "flake8>=5.0.0",
    "mypy>=0.991",
]
test = [
    "pytest>=7.2.0",
    "pytest-mock>=3.10.0",
    "factory-boy>=3.2.0",
]
```

### 3. バージョンの適切な固定
```txt
# requirements.txt - セマンティックバージョニング
# 完全固定（推奨：再現性が高い）
django==4.1.7
requests==2.28.2

# マイナーバージョンまで許可
django~=4.1.0    # 4.1.x は許可、4.2.0 は不可
requests~=2.28.0

# 範囲指定
django>=4.1.0,<5.0.0
numpy>=1.23.0,<1.24.0

# requirements.inとpip-compileの使用
# requirements.in
django~=4.1.0
requests
```

### 4. 仮想環境とツールの活用
```bash
# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# pip-toolsを使った依存関係管理
pip install pip-tools

# requirements.inから requirements.txt を生成
pip-compile requirements.in

# 依存関係の更新
pip-compile --upgrade requirements.in

# 未使用パッケージの検出
pip install pip-autoremove
pip-autoremove -L  # 未使用パッケージをリスト表示
```

### 5. 依存関係の監査
```python
# check_dependencies.py
import ast
import os
from pathlib import Path

def find_imports(directory):
    """プロジェクト内のすべてのインポートを収集"""
    imports = set()
    for py_file in Path(directory).rglob("*.py"):
        with open(py_file, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0])
            except SyntaxError:
                pass
    return imports

# 使用例
used_packages = find_imports("src/")
print(f"使用中のパッケージ: {sorted(used_packages)}")
```

## ベストプラクティス

1. **依存関係の最小化**: 本当に必要なパッケージのみを含める
2. **バージョンの固定**: 本番環境では完全にバージョンを固定
3. **開発/本番の分離**: requirements-dev.txtやpyproject.tomlの optional-dependencies を活用
4. **定期的な更新**: セキュリティパッチのために定期的に依存関係を更新
5. **ライセンスの確認**: 使用するパッケージのライセンスがプロジェクトと互換性があることを確認
6. **CI/CDでの検証**: 依存関係の問題を自動的に検出
7. **ロックファイルの使用**: pip-tools、Poetry、Pipenvなどでロックファイルを生成