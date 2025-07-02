"""廃止予定機能の使用を検出するチェッカー."""

import ast
import sys
from typing import ClassVar, Dict, List, Optional, Set, Union

from src_check.core.base import BaseChecker
from src_check.models.check_result import CheckResult, FailureLocation, Severity


class DeprecationChecker(BaseChecker):
    """廃止予定機能の使用を検出するチェッカー."""

    @property
    def name(self) -> str:
        """チェッカーの名前を返す."""
        return "deprecation"

    @property
    def description(self) -> str:
        """チェッカーの説明を返す."""
        return "廃止予定機能の使用を検出"

    @property
    def category(self) -> str:
        """チェッカーのカテゴリを返す."""
        return "code_quality"

    # Python標準ライブラリの廃止予定モジュール/関数
    DEPRECATED_MODULES: ClassVar[Dict[str, str]] = {
        "imp": "importlib",
        "asyncore": "asyncio",
        "asynchat": "asyncio",
        "smtpd": "aiosmtpd or other alternatives",
    }

    # collections の古いAPI
    DEPRECATED_COLLECTIONS: ClassVar[Dict[str, str]] = {
        "MutableMapping": "collections.abc.MutableMapping",
        "MutableSet": "collections.abc.MutableSet",
        "MutableSequence": "collections.abc.MutableSequence",
        "Mapping": "collections.abc.Mapping",
        "Set": "collections.abc.Set",
        "Sequence": "collections.abc.Sequence",
        "Iterable": "collections.abc.Iterable",
        "Iterator": "collections.abc.Iterator",
        "Generator": "collections.abc.Generator",
        "Callable": "collections.abc.Callable",
    }

    # typing モジュールの古い書き方 (Python 3.9+)
    DEPRECATED_TYPING: ClassVar[Dict[str, str]] = {
        "List": "list",
        "Dict": "dict",
        "Set": "set",
        "Tuple": "tuple",
        "Type": "type",
        "FrozenSet": "frozenset",
    }

    # asyncioの古いAPI
    DEPRECATED_ASYNCIO: ClassVar[Dict[str, str]] = {
        "ensure_future": "create_task",
        "@coroutine": "async def",
    }

    def __init__(self) -> None:
        """初期化."""
        super().__init__()
        self.deprecated_imports: Set[str] = set()
        self.current_module: str = ""
        self.has_future_annotations = False

    def check(self, ast_tree: ast.AST, file_path: str) -> Optional[CheckResult]:
        """ASTをチェックして廃止予定機能の使用を検出する."""
        self.current_module = file_path
        self.deprecated_imports.clear()
        self.has_future_annotations = False

        # future annotationsのインポートをチェック
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                for alias in node.names:
                    if alias.name == "annotations":
                        self.has_future_annotations = True
                        break

        visitor = DeprecationVisitor(self)
        visitor.visit(ast_tree)

        if not visitor.failures:
            return None

        result = self.create_result()
        result.failure_locations = visitor.failures
        return result


class DeprecationVisitor(ast.NodeVisitor):
    """ASTを訪問して廃止予定機能を検出するビジター."""

    def __init__(self, checker: DeprecationChecker) -> None:
        """初期化."""
        self.checker = checker
        self.failures: List[FailureLocation] = []
        self.current_function: str = ""
        self.import_map: Dict[str, str] = {}  # alias -> module mapping

    def add_failure(
        self,
        node: Union[
            ast.Import,
            ast.ImportFrom,
            ast.FunctionDef,
            ast.AsyncFunctionDef,
            ast.Call,
            ast.BinOp,
            ast.Attribute,
        ],
        message: str,
        severity: Severity = Severity.MEDIUM,
    ) -> None:
        """失敗を追加する."""
        self.failures.append(
            FailureLocation(
                file_path=self.checker.current_module,
                line=node.lineno,
                column=node.col_offset,
                message=message,
            )
        )

    def visit_Import(self, node: ast.Import) -> None:
        """importステートメントを訪問."""
        for alias in node.names:
            module_name = alias.name
            import_alias = alias.asname or alias.name
            self.import_map[import_alias] = module_name

            # DEPR001: 廃止予定モジュールのインポート
            if module_name in DeprecationChecker.DEPRECATED_MODULES:
                replacement = DeprecationChecker.DEPRECATED_MODULES[module_name]
                self.add_failure(
                    node,
                    f"DEPR001: 廃止予定のモジュール '{module_name}' を使用しています。'{replacement}' を使用してください",
                    Severity.MEDIUM,
                )
                self.checker.deprecated_imports.add(module_name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """from-importステートメントを訪問."""
        if not node.module:
            self.generic_visit(node)
            return

        # DEPR001: 廃止予定モジュールからのインポート
        if node.module in DeprecationChecker.DEPRECATED_MODULES:
            replacement = DeprecationChecker.DEPRECATED_MODULES[node.module]
            self.add_failure(
                node,
                f"DEPR001: 廃止予定のモジュール '{node.module}' を使用しています。'{replacement}' を使用してください",
                Severity.MEDIUM,
            )
            self.checker.deprecated_imports.add(node.module)

        # DEPR001: collectionsの古いAPI
        if node.module == "collections" and node.names:
            for alias in node.names:
                if (
                    isinstance(alias.name, str)
                    and alias.name in DeprecationChecker.DEPRECATED_COLLECTIONS
                ):
                    replacement = DeprecationChecker.DEPRECATED_COLLECTIONS[alias.name]
                    self.add_failure(
                        node,
                        f"DEPR001: '{node.module}.{alias.name}' は廃止予定です。'{replacement}' を使用してください",
                        Severity.MEDIUM,
                    )

        # DEPR005: typingモジュールの古い書き方（Python 3.9+）
        if (
            node.module == "typing"
            and sys.version_info >= (3, 9)
            and not self.checker.has_future_annotations
        ):
            for alias in node.names:
                if (
                    isinstance(alias.name, str)
                    and alias.name in DeprecationChecker.DEPRECATED_TYPING
                ):
                    replacement = DeprecationChecker.DEPRECATED_TYPING[alias.name]
                    self.add_failure(
                        node,
                        f"DEPR005: Python 3.9+では 'typing.{alias.name}' の代わりに '{replacement}' を使用できます",
                        Severity.INFO,
                    )

        # DEPR006: from module import * の使用
        if any(alias.name == "*" for alias in node.names):
            self.add_failure(
                node,
                "DEPR006: 'from module import *' は推奨されません。明示的なインポートを使用してください",
                Severity.MEDIUM,
            )

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """関数定義を訪問."""
        old_function = self.current_function
        self.current_function = node.name

        # DEPR002: @deprecatedデコレータまたはDeprecationWarningを含む関数の検出
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "deprecated":
                # この関数自体が廃止予定としてマークされている
                pass
            elif isinstance(decorator, ast.Attribute) and decorator.attr == "coroutine":
                # DEPR004: asyncio.coroutineデコレータの使用
                self.add_failure(
                    decorator,
                    "DEPR004: '@coroutine' デコレータは廃止予定です。'async def' を使用してください",
                    Severity.MEDIUM,
                )

        self.generic_visit(node)
        self.current_function = old_function

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """非同期関数定義を訪問."""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_Call(self, node: ast.Call) -> None:
        """関数呼び出しを訪問."""
        # DEPR002: warnings.warnでDeprecationWarningを発行している関数の呼び出し
        if isinstance(node.func, ast.Attribute):
            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "warnings"
                and node.func.attr == "warn"
            ):
                # DeprecationWarningを確認
                for arg in node.args:
                    if isinstance(arg, ast.Name) and arg.id == "DeprecationWarning":
                        # この呼び出し自体は廃止予定の宣言なのでスキップ
                        pass

            # DEPR004: asyncio.ensure_futureの使用
            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "asyncio"
                and node.func.attr == "ensure_future"
            ):
                self.add_failure(
                    node,
                    "DEPR004: 'asyncio.ensure_future' は 'asyncio.create_task' を使用することが推奨されます",
                    Severity.INFO,
                )

        # DEPR003: 文字列フォーマットの古い書き方
        if isinstance(node.func, ast.Attribute) and node.func.attr == "__mod__":
            if isinstance(node.func.value, ast.Str):
                self.add_failure(
                    node,
                    "DEPR003: '%' による文字列フォーマットは古い書き方です。f-stringまたは.format()を使用してください",
                    Severity.INFO,
                )

        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        """二項演算を訪問."""
        # DEPR003: % による文字列フォーマット
        if isinstance(node.op, ast.Mod) and isinstance(node.left, ast.Str):
            self.add_failure(
                node,
                "DEPR003: '%' による文字列フォーマットは古い書き方です。f-stringまたは.format()を使用してください",
                Severity.INFO,
            )
        self.generic_visit(node)
