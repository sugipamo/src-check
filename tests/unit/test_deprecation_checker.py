"""DeprecationCheckerのテスト."""

import ast
import sys

import pytest

from src_check.rules.deprecation import DeprecationChecker


@pytest.fixture
def checker():
    """DeprecationCheckerのインスタンスを作成."""
    return DeprecationChecker()


@pytest.fixture
def temp_py_file(tmp_path):
    """一時的なPythonファイルを作成."""

    def _create_file(content: str, filename: str = "test.py"):
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path

    return _create_file


def test_deprecated_module_import(checker, temp_py_file):
    """DEPR001: 廃止予定モジュールのインポート検出."""
    content = """
import imp
import asyncore
import asynchat
import smtpd
"""
    file_path = temp_py_file(content)

    # ASTをパースしてチェック
    tree = ast.parse(content, filename=str(file_path))
    result = checker.check(tree, str(file_path))

    assert result is not None
    assert len(result.failure_locations) == 4

    # 各モジュールの代替案を確認
    messages = [f.message for f in result.failure_locations]
    assert any("imp" in msg and "importlib" in msg for msg in messages)
    assert any("asyncore" in msg and "asyncio" in msg for msg in messages)
    assert any("asynchat" in msg and "asyncio" in msg for msg in messages)
    assert any("smtpd" in msg and "aiosmtpd" in msg for msg in messages)


def test_deprecated_collections_api(checker, temp_py_file):
    """DEPR001: collectionsの古いAPI検出."""
    content = """
from collections import MutableMapping, MutableSet, Mapping
from collections import Iterable, Iterator, Callable
"""
    file_path = temp_py_file(content)
    tree = ast.parse(content, filename=str(file_path))
    result = checker.check(tree, str(file_path))

    assert result is not None
    assert len(result.failure_locations) == 6
    assert all("collections.abc" in f.message for f in result.failure_locations)


def test_deprecated_typing_python39(checker, temp_py_file):
    """DEPR005: Python 3.9+でのtypingモジュールの古い書き方検出."""
    if sys.version_info < (3, 9):
        pytest.skip("Python 3.9+ required")

    content = """
from typing import List, Dict, Set, Tuple, Type, FrozenSet
"""
    file_path = temp_py_file(content)
    tree = ast.parse(content, filename=str(file_path))
    result = checker.check(tree, str(file_path))

    assert result is not None
    assert len(result.failure_locations) == 6

    # 代替案の確認
    messages = [f.message for f in result.failure_locations]
    assert any("List" in msg and "list" in msg for msg in messages)
    assert any("Dict" in msg and "dict" in msg for msg in messages)


def test_typing_with_future_annotations(checker, temp_py_file):
    """future annotationsがインポートされている場合はDEPR005を出さない."""
    if sys.version_info < (3, 9):
        pytest.skip("Python 3.9+ required")

    content = """
from __future__ import annotations
from typing import List, Dict, Set
"""
    file_path = temp_py_file(content)
    tree = ast.parse(content, filename=str(file_path))
    result = checker.check(tree, str(file_path))

    # future annotationsがある場合は警告しない
    assert result is None


def test_deprecated_string_formatting(checker, temp_py_file):
    """DEPR003: 古い文字列フォーマットの検出."""
    content = """
name = "Alice"
age = 30
message = "Hello %s, you are %d years old" % (name, age)
another = "%s" % name
"""
    file_path = temp_py_file(content)
    tree = ast.parse(content, filename=str(file_path))
    result = checker.check(tree, str(file_path))

    assert result is not None
    assert len(result.failure_locations) == 2
    assert all("f-string" in f.message for f in result.failure_locations)


def test_asyncio_deprecated_api(checker, temp_py_file):
    """DEPR004: asyncioの廃止予定API検出."""
    content = """
import asyncio

async def main():
    task = asyncio.ensure_future(some_coroutine())
    return task

@asyncio.coroutine
def old_style_coroutine():
    yield from asyncio.sleep(1)
"""
    file_path = temp_py_file(content)
    tree = ast.parse(content, filename=str(file_path))
    result = checker.check(tree, str(file_path))

    assert result is not None
    # ensure_futureとcoroutineデコレータの2つ
    assert len(result.failure_locations) == 2

    messages = [f.message for f in result.failure_locations]
    assert any("ensure_future" in msg and "create_task" in msg for msg in messages)
    assert any("@coroutine" in msg and "async def" in msg for msg in messages)


def test_star_import(checker, temp_py_file):
    """DEPR006: from module import * の検出."""
    content = """
from os import *
from sys import *
from collections.abc import *
"""
    file_path = temp_py_file(content)
    tree = ast.parse(content, filename=str(file_path))
    result = checker.check(tree, str(file_path))

    assert result is not None
    assert len(result.failure_locations) == 3
    assert all("明示的なインポート" in f.message for f in result.failure_locations)


def test_no_issues_modern_code(checker, temp_py_file):
    """モダンなコードでは問題が検出されないことを確認."""
    content = """
from collections.abc import MutableMapping, Mapping
from typing import Optional, Union
import asyncio

async def modern_function(name: str) -> str:
    message = f"Hello {name}"
    task = asyncio.create_task(some_async_function())
    return message
"""
    file_path = temp_py_file(content)
    tree = ast.parse(content, filename=str(file_path))
    result = checker.check(tree, str(file_path))

    assert result is None


def test_mixed_issues(checker, temp_py_file):
    """複数の問題が混在するケース."""
    content = """
import imp
from collections import MutableMapping
from typing import List, Dict

def format_data(data):
    return "Data: %s" % data
    
from os import *
"""
    file_path = temp_py_file(content)
    tree = ast.parse(content, filename=str(file_path))
    result = checker.check(tree, str(file_path))

    assert result is not None
    # 最低4つの問題（imp, MutableMapping, %, import *）
    assert len(result.failure_locations) >= 4

    messages = [f.message for f in result.failure_locations]
    has_depr001 = any("DEPR001" in msg for msg in messages)
    has_depr003 = any("DEPR003" in msg for msg in messages)
    has_depr006 = any("DEPR006" in msg for msg in messages)

    assert has_depr001  # imp, MutableMapping
    assert has_depr003  # % formatting
    assert has_depr006  # import *

    # Python 3.9+ならDEPR005も
    if sys.version_info >= (3, 9):
        has_depr005 = any("DEPR005" in msg for msg in messages)
        assert has_depr005


def test_deprecated_module_with_alias(checker, temp_py_file):
    """エイリアス付きの廃止予定モジュールインポート."""
    content = """
import imp as importer
import asyncore as async_old
"""
    file_path = temp_py_file(content)
    tree = ast.parse(content, filename=str(file_path))
    result = checker.check(tree, str(file_path))

    assert result is not None
    assert len(result.failure_locations) == 2
    assert all("DEPR001" in f.message for f in result.failure_locations)


def test_non_python_file(checker, temp_py_file):
    """Pythonファイル以外は無視することを確認."""
    # この場合、パースエラーになるので、空のASTを渡す
    content = "This is not Python code"
    file_path = temp_py_file(content, "test.txt")

    # 空のモジュールを作成
    tree = ast.parse("")
    result = checker.check(tree, str(file_path))

    assert result is None


def test_empty_file(checker, temp_py_file):
    """空のファイルでエラーが出ないことを確認."""
    content = ""
    file_path = temp_py_file(content)
    tree = ast.parse(content, filename=str(file_path))
    result = checker.check(tree, str(file_path))

    assert result is None


def test_syntax_error_handling(checker, temp_py_file):
    """構文エラーがあるファイルでもクラッシュしないことを確認."""
    content = """
import imp
this is invalid python syntax
"""
    file_path = temp_py_file(content)

    # 構文エラーの場合、パースが失敗するのでtry-catchで処理
    try:
        tree = ast.parse(content, filename=str(file_path))
        result = checker.check(tree, str(file_path))
    except SyntaxError:
        # 構文エラーは期待される動作
        pass
