#!/bin/bash

# 仮想環境クリーンアップスクリプト
# src-check プロジェクト用

echo "🧹 仮想環境クリーンアップスクリプト"
echo "========================================"

# プロジェクトルートディレクトリの確認
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "📍 プロジェクトルート: $PROJECT_ROOT"

# 保持すべき仮想環境
KEEP_VENVS=(
    ".venv"                  # メイン開発環境
    "test-install/venv"      # インストールテスト環境
    "test-pypi-install/venv" # PyPIテスト環境
)

echo ""
echo "✅ 保持される仮想環境:"
for venv in "${KEEP_VENVS[@]}"; do
    if [ -d "$PROJECT_ROOT/$venv" ]; then
        echo "   - $venv ✅"
    else
        echo "   - $venv ❌ (存在しません)"
    fi
done

echo ""
echo "🔍 削除対象の仮想環境を検索中..."

# 削除対象の仮想環境を見つける
DELETE_CANDIDATES=()
while IFS= read -r -d '' venv_dir; do
    # 相対パスに変換
    rel_path="${venv_dir#$PROJECT_ROOT/}"
    
    # 保持リストにあるかチェック
    should_keep=false
    for keep_venv in "${KEEP_VENVS[@]}"; do
        if [ "$rel_path" = "$keep_venv" ]; then
            should_keep=true
            break
        fi
    done
    
    # 保持すべきでない場合は削除候補に追加
    if [ "$should_keep" = false ]; then
        DELETE_CANDIDATES+=("$rel_path")
    fi
done < <(find "$PROJECT_ROOT" -type d \( -name "*venv*" -o -name "*env" \) -print0 2>/dev/null)

if [ ${#DELETE_CANDIDATES[@]} -eq 0 ]; then
    echo "✨ 削除対象の仮想環境はありません。"
    exit 0
fi

echo ""
echo "⚠️  削除対象の仮想環境:"
for candidate in "${DELETE_CANDIDATES[@]}"; do
    echo "   - $candidate"
done

echo ""
read -p "❓ これらの仮想環境を削除しますか？ [y/N]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "🚫 削除をキャンセルしました。"
    exit 0
fi

echo ""
echo "🗑️  仮想環境を削除中..."

deleted_count=0
for candidate in "${DELETE_CANDIDATES[@]}"; do
    full_path="$PROJECT_ROOT/$candidate"
    if [ -d "$full_path" ]; then
        echo "   削除中: $candidate"
        rm -rf "$full_path"
        if [ $? -eq 0 ]; then
            ((deleted_count++))
            echo "   ✅ 削除完了: $candidate"
        else
            echo "   ❌ 削除失敗: $candidate"
        fi
    else
        echo "   ⚠️  存在しません: $candidate"
    fi
done

echo ""
echo "🎉 クリーンアップ完了！"
echo "   削除した仮想環境数: $deleted_count"

# ディスクスペースの確認
echo ""
echo "💾 ディスクスペース使用量:"
du -sh "$PROJECT_ROOT" 2>/dev/null || echo "   使用量の取得に失敗しました"

echo ""
echo "📝 推奨事項:"
echo "   - 今後は .venv ディレクトリを統一使用してください"
echo "   - 定期的にこのスクリプトを実行してください"
echo "   - 新しい仮想環境は python -m venv .venv で作成してください"

echo ""
echo "✨ 完了しました！"