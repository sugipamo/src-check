#!/bin/bash
# GitHub Release作成スクリプト

set -e

echo "=== GitHub Release作成ガイド ==="
echo ""
echo "このスクリプトは、GitHub Releaseを作成するための手順を案内します。"
echo ""

# タグの確認
echo "1. Gitタグの確認"
echo "   現在のタグ:"
git tag -l | grep -E "^v[0-9]" | tail -5
echo ""

if ! git tag -l | grep -q "^v0.2.0$"; then
    echo "   ⚠️  v0.2.0タグが見つかりません。"
    echo "   タグを作成してプッシュしてください:"
    echo "     git tag v0.2.0"
    echo "     git push origin v0.2.0"
else
    echo "   ✓ v0.2.0タグが存在します"
fi

echo ""
echo "2. GitHub Releaseページへのアクセス"
echo "   以下のURLを開いてください:"
echo "   https://github.com/yourusername/src-check/releases/new"
echo ""

echo "3. Release作成フォームの入力"
echo ""
echo "   Tag: v0.2.0"
echo "   Target: main (またはデフォルトブランチ)"
echo "   Release title: src-check v0.2.0 - Functional Release"
echo ""
echo "   Release notes:"
echo "   (RELEASE_NOTES_v0.2.0.mdの内容をコピー＆ペースト)"
echo ""

echo "4. アセットの添付"
echo "   以下のファイルをドラッグ＆ドロップで添付:"
ls -la dist/*.whl dist/*.tar.gz
echo ""

echo "5. リリースタイプの選択"
echo "   ✓ Set as a pre-release のチェックは外す"
echo "   ✓ Set as the latest release にチェック"
echo ""

echo "6. 公開"
echo "   'Publish release'ボタンをクリック"
echo ""

echo "=== 追加の手順 ==="
echo ""
echo "リリース後の確認事項:"
echo "1. リリースページが正しく表示されるか"
echo "2. アセットがダウンロード可能か"
echo "3. READMEのインストール手順が最新か"
echo ""

# ghコマンドが利用可能な場合の自動化オプション
if command -v gh &> /dev/null; then
    echo "=== GitHub CLIを使用した自動作成 ==="
    echo ""
    echo "GitHub CLI (gh) がインストールされています。"
    echo "以下のコマンドで自動的にリリースを作成できます:"
    echo ""
    echo "gh release create v0.2.0 \\"
    echo "  --title 'src-check v0.2.0 - Functional Release' \\"
    echo "  --notes-file RELEASE_NOTES_v0.2.0.md \\"
    echo "  dist/src_check-0.2.0-py3-none-any.whl \\"
    echo "  dist/src_check-0.2.0.tar.gz"
    echo ""
    read -p "GitHub CLIでリリースを作成しますか？ (y/n): " use_gh
    
    if [ "$use_gh" = "y" ]; then
        echo "リリースを作成中..."
        gh release create v0.2.0 \
          --title "src-check v0.2.0 - Functional Release" \
          --notes-file RELEASE_NOTES_v0.2.0.md \
          dist/src_check-0.2.0-py3-none-any.whl \
          dist/src_check-0.2.0.tar.gz
        echo "✓ リリースが作成されました！"
    fi
else
    echo "ヒント: GitHub CLI (gh) をインストールすると、リリース作成を自動化できます。"
    echo "  インストール: https://cli.github.com/"
fi