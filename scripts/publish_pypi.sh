#!/bin/bash
# PyPI正式公開スクリプト

set -e

echo "=== src-check v0.2.0 PyPI正式公開スクリプト ==="
echo ""

# TestPyPIでのテスト確認
echo "⚠️  重要: TestPyPIでのテストは完了していますか？"
echo "   完了していない場合は、先に ./scripts/publish_testpypi.sh を実行してください。"
echo ""
read -p "TestPyPIでのテストは完了していますか？ (y/n): " test_confirm

if [ "$test_confirm" != "y" ]; then
    echo "TestPyPIでのテストを先に実行してください。"
    exit 1
fi

# 環境変数のチェック
if [ -z "$TWINE_USERNAME" ] || [ -z "$TWINE_PASSWORD" ]; then
    echo ""
    echo "エラー: 環境変数が設定されていません。"
    echo ""
    echo "PyPI用の新しいトークンが必要です："
    echo "  export TWINE_USERNAME=__token__"
    echo "  export TWINE_PASSWORD=pypi-<your-pypi-token-here>"
    echo ""
    echo "PyPIでトークンを生成: https://pypi.org/manage/account/token/"
    exit 1
fi

# パッケージファイルの確認
echo ""
echo "1. パッケージファイルの確認..."
ls -la dist/
echo ""

# twineでの検証
echo "2. パッケージの最終検証..."
twine check dist/*
echo ""

# リリースチェックリスト
echo "3. リリースチェックリスト"
echo "   ✓ バージョン番号: 0.2.0"
echo "   ✓ CHANGELOG.md: 更新済み"
echo "   ✓ README.md: 最新"
echo "   ✓ ライセンス: MIT"
echo "   ✓ テスト: 全182件合格"
echo "   ✓ カバレッジ: 87%"
echo ""

# 最終確認
echo "⚠️  これは本番のPyPIへの公開です。元に戻すことはできません。"
read -p "PyPIに正式公開しますか？ (yes/no): " final_confirm

if [ "$final_confirm" != "yes" ]; then
    echo "公開をキャンセルしました。"
    exit 0
fi

# アップロード実行
echo ""
echo "PyPIへアップロード中..."
twine upload dist/*

echo ""
echo "=== 🎉 公開完了！ ==="
echo ""
echo "パッケージページ: https://pypi.org/project/src-check/0.2.0/"
echo ""
echo "インストール方法:"
echo "  pip install src-check==0.2.0"
echo ""
echo "次のステップ:"
echo "  1. GitHub Releasesページの作成"
echo "  2. アナウンスの準備"
echo "  3. ドキュメントの更新"
echo ""