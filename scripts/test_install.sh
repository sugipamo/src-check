#!/bin/bash
# TestPyPI/PyPIからのインストールテストスクリプト

set -e

echo "=== src-check インストールテストスクリプト ==="
echo ""

# 引数の確認
if [ "$1" = "testpypi" ]; then
    REPO="testpypi"
    PIP_ARGS="-i https://test.pypi.org/simple/"
    echo "TestPyPIからインストールします"
elif [ "$1" = "pypi" ] || [ -z "$1" ]; then
    REPO="pypi"
    PIP_ARGS=""
    echo "PyPIからインストールします"
else
    echo "使用方法: $0 [testpypi|pypi]"
    exit 1
fi

# テスト用仮想環境の作成
TEST_ENV="test-install-env-$$"
echo ""
echo "1. テスト用仮想環境を作成: $TEST_ENV"
python -m venv $TEST_ENV

# 仮想環境の有効化
echo "2. 仮想環境を有効化"
source $TEST_ENV/bin/activate

# pipのアップグレード
echo "3. pipをアップグレード"
pip install --upgrade pip

# src-checkのインストール
echo ""
echo "4. src-checkをインストール"
pip install $PIP_ARGS src-check==0.2.0

# インストール確認
echo ""
echo "5. インストール確認"
echo "  - バージョン確認:"
src-check --version

echo ""
echo "  - コマンド確認:"
which src-check
which src-check-kpi

echo ""
echo "  - ヘルプ表示:"
src-check --help | head -20

# 簡単な動作テスト
echo ""
echo "6. 動作テスト"

# テスト用のPythonファイルを作成
TEST_DIR="$TEST_ENV/test_project"
mkdir -p $TEST_DIR
cat > $TEST_DIR/test.py << 'EOF'
"""Test module for src-check."""

def hello_world():
    """Print hello world."""
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
EOF

echo "  - テストファイルでの実行:"
src-check $TEST_DIR/

echo ""
echo "  - KPIスコア計算:"
src-check-kpi $TEST_DIR/

# クリーンアップ
echo ""
echo "7. クリーンアップ"
deactivate
rm -rf $TEST_ENV

echo ""
echo "=== テスト完了 ==="
echo "src-check v0.2.0 は正常にインストールされ、動作することを確認しました。"