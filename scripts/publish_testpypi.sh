#!/bin/bash
# TestPyPI公開スクリプト

set -e  # エラーで停止

echo "=== src-check v0.2.0 TestPyPI公開スクリプト ==="
echo ""

# 環境変数のチェック
if [ -z "$TWINE_USERNAME" ] || [ -z "$TWINE_PASSWORD" ]; then
    echo "エラー: 環境変数が設定されていません。"
    echo ""
    echo "以下のコマンドを実行してください："
    echo "  export TWINE_USERNAME=__token__"
    echo "  export TWINE_PASSWORD=pypi-<your-token-here>"
    echo ""
    echo "TestPyPIでトークンを生成: https://test.pypi.org/manage/account/token/"
    exit 1
fi

# パッケージファイルの確認
echo "1. パッケージファイルの確認..."
if [ ! -f "dist/src_check-0.2.0-py3-none-any.whl" ] || [ ! -f "dist/src_check-0.2.0.tar.gz" ]; then
    echo "エラー: distディレクトリにパッケージファイルが見つかりません。"
    echo "python -m build を実行してください。"
    exit 1
fi

echo "  ✓ パッケージファイルを確認しました"
ls -la dist/
echo ""

# twineでの検証
echo "2. パッケージの検証..."
twine check dist/*
echo ""

# アップロード確認
echo "3. TestPyPIへのアップロード"
echo "   URL: https://test.pypi.org/"
echo ""
read -p "TestPyPIにアップロードしますか？ (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "アップロードをキャンセルしました。"
    exit 0
fi

# アップロード実行
echo ""
echo "アップロードを実行中..."
twine upload --repository testpypi dist/*

echo ""
echo "=== アップロード完了 ==="
echo ""
echo "パッケージページ: https://test.pypi.org/project/src-check/0.2.0/"
echo ""
echo "インストールテスト方法:"
echo "  pip install -i https://test.pypi.org/simple/ src-check==0.2.0"
echo ""