# src-check セキュリティ移行計画

## 概要
動的インポートから静的解析への移行により、パッケージ配布時のセキュリティリスクを排除します。

## 現在の問題点

### 1. 動的インポートのリスク
- **任意コード実行**: `importlib.import_module`による悪意のあるコードの実行可能性
- **サンドボックス回避**: 名前空間の分離だけでは完全な隔離が困難
- **予測不可能な副作用**: インポート時の副作用による環境汚染
- **依存関係の汚染**: 動的にロードされたモジュールが他のモジュールに影響

### 2. パッケージ配布上の懸念
- pipでインストールしたツールが任意のコードを実行することへのユーザーの不信感
- セキュリティ監査での指摘リスク
- 企業環境での採用障壁

## 移行計画

### Phase 1: アーキテクチャ設計変更（1週間）

#### 1.1 プラグインシステムの再設計
```python
# src_check/core/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import ast

@dataclass
class CheckResult:
    """チェック結果のデータクラス"""
    title: str
    failure_locations: List[dict]
    fix_policy: str
    fix_example_code: Optional[str] = None
    severity: str = "medium"

class BaseChecker(ABC):
    """全てのチェッカーの基底クラス"""
    
    @abstractmethod
    def check(self, ast_tree: ast.AST, file_path: str) -> CheckResult:
        """ASTを解析してチェック結果を返す"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """チェッカーの名前"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """チェッカーの説明"""
        pass
```

#### 1.2 プラグインレジストリ
```python
# src_check/core/registry.py
from typing import Dict, Type
from src_check.core.base import BaseChecker
import pkg_resources

class CheckerRegistry:
    """チェッカーの登録と管理"""
    
    def __init__(self):
        self._checkers: Dict[str, Type[BaseChecker]] = {}
        self._load_builtin_checkers()
        self._load_plugin_checkers()
    
    def _load_builtin_checkers(self):
        """ビルトインチェッカーの読み込み"""
        from src_check.rules import (
            SecurityChecker,
            ArchitectureChecker,
            CodeQualityChecker,
            TestQualityChecker
        )
        
        for checker_class in [
            SecurityChecker,
            ArchitectureChecker, 
            CodeQualityChecker,
            TestQualityChecker
        ]:
            self.register(checker_class)
    
    def _load_plugin_checkers(self):
        """エントリーポイントからプラグインチェッカーを読み込み"""
        for entry_point in pkg_resources.iter_entry_points('src_check.rules'):
            try:
                checker_class = entry_point.load()
                if issubclass(checker_class, BaseChecker):
                    self.register(checker_class)
            except Exception as e:
                # ログに記録して続行
                print(f"Failed to load plugin {entry_point.name}: {e}")
    
    def register(self, checker_class: Type[BaseChecker]):
        """チェッカーを登録"""
        instance = checker_class()
        self._checkers[instance.name] = checker_class
    
    def get_all_checkers(self) -> Dict[str, Type[BaseChecker]]:
        """全てのチェッカーを取得"""
        return self._checkers.copy()
```

### Phase 2: AST解析エンジンの実装（1週間）

#### 2.1 静的解析エンジン
```python
# src_check/core/ast_analyzer.py
import ast
from pathlib import Path
from typing import List, Dict, Any
from src_check.core.registry import CheckerRegistry
from src_check.core.base import CheckResult

class ASTAnalyzer:
    """AST解析エンジン"""
    
    def __init__(self, registry: CheckerRegistry):
        self.registry = registry
        self._ast_cache: Dict[str, ast.AST] = {}
    
    def analyze_file(self, file_path: Path) -> List[CheckResult]:
        """ファイルを解析してチェック結果を返す"""
        # ASTのパース（キャッシュ利用）
        ast_tree = self._get_or_parse_ast(file_path)
        if not ast_tree:
            return []
        
        # 全てのチェッカーを実行
        results = []
        for name, checker_class in self.registry.get_all_checkers().items():
            try:
                checker = checker_class()
                result = checker.check(ast_tree, str(file_path))
                if result and result.failure_locations:
                    results.append(result)
            except Exception as e:
                # エラーをログに記録して続行
                print(f"Checker {name} failed on {file_path}: {e}")
        
        return results
    
    def _get_or_parse_ast(self, file_path: Path) -> Optional[ast.AST]:
        """ASTをパースまたはキャッシュから取得"""
        cache_key = str(file_path)
        
        if cache_key in self._ast_cache:
            return self._ast_cache[cache_key]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ast_tree = ast.parse(content, filename=str(file_path))
            self._ast_cache[cache_key] = ast_tree
            return ast_tree
        except Exception:
            return None
```

### Phase 3: 既存ルールの移行（2週間）

#### 3.1 ルール実装例
```python
# src_check/rules/security.py
import ast
from src_check.core.base import BaseChecker, CheckResult

class SecurityChecker(BaseChecker):
    """セキュリティ関連のチェック"""
    
    @property
    def name(self) -> str:
        return "security"
    
    @property 
    def description(self) -> str:
        return "Security vulnerability detection"
    
    def check(self, ast_tree: ast.AST, file_path: str) -> CheckResult:
        visitor = SecurityVisitor(file_path)
        visitor.visit(ast_tree)
        
        return CheckResult(
            title="Security Issues",
            failure_locations=visitor.issues,
            fix_policy="Remove hardcoded secrets and use environment variables",
            severity="high" if visitor.issues else "info"
        )

class SecurityVisitor(ast.NodeVisitor):
    """セキュリティ問題を検出するASTビジター"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues = []
    
    def visit_Assign(self, node: ast.Assign):
        """代入文をチェック"""
        # ハードコードされたシークレットの検出
        for target in node.targets:
            if isinstance(target, ast.Name):
                if any(secret in target.id.lower() for secret in [
                    'password', 'secret', 'token', 'api_key'
                ]):
                    if isinstance(node.value, ast.Constant):
                        self.issues.append({
                            'file': self.file_path,
                            'line': node.lineno,
                            'column': node.col_offset,
                            'message': f'Hardcoded secret: {target.id}'
                        })
        
        self.generic_visit(node)
```

### Phase 4: 設定ファイルベースの制御（1週間）

#### 4.1 設定ファイル形式
```yaml
# .src-check.yaml
rules:
  # ビルトインルール
  - name: security
    enabled: true
    severity_override: critical
    
  - name: architecture
    enabled: true
    options:
      max_import_depth: 5
      
  - name: code_quality
    enabled: true
    
  - name: test_quality
    enabled: false  # 無効化
    
  # 外部プラグイン
  - name: custom_checker
    enabled: true
    plugin: my-custom-plugin  # pip install my-custom-plugin

# グローバル設定
exclude_patterns:
  - "**/__pycache__/**"
  - "**/venv/**"
  - "**/.git/**"

output:
  format: json
  file: .src-check-results/report.json
```

### Phase 5: 後方互換性とマイグレーション（1週間）

#### 5.1 移行ツール
```python
# src_check/migration/converter.py
"""既存のプロセッサーを新形式に変換するツール"""

def convert_processor_to_checker(processor_path: Path) -> str:
    """既存のmain.py形式を新しいChecker形式に変換"""
    # AST変換によるコード生成
    # main()関数をcheck()メソッドに変換
    pass

def generate_entry_point(checker_module: str) -> str:
    """pyproject.tomlのエントリーポイント設定を生成"""
    pass
```

## セキュリティ上の利点

1. **コード実行の排除**: 全ての解析がAST上で行われ、実際のコード実行なし
2. **予測可能な動作**: 登録されたチェッカーのみが実行される
3. **監査可能性**: 全てのチェッカーが明示的に登録される
4. **隔離性**: チェッカー間の相互影響なし
5. **署名検証可能**: 将来的にプラグインの署名検証を追加可能

## 実装スケジュール

- **Week 1**: アーキテクチャ設計とコア実装
- **Week 2**: AST解析エンジンとレジストリ
- **Week 3-4**: 既存ルールの移行
- **Week 5**: 設定管理と統合テスト
- **Week 6**: 後方互換性とドキュメント

## 成功指標

- ✅ 動的インポートの完全排除
- ✅ 既存機能の100%維持
- ✅ パフォーマンス劣化なし（むしろ向上）
- ✅ セキュリティ監査でのグリーンライト
- ✅ 企業環境での採用可能性向上