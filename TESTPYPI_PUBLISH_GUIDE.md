# TestPyPI 公開ガイド

このガイドは、src-check v0.2.0をTestPyPIに公開するための手順を説明します。

## 前提条件

- TestPyPIアカウントが必要です: https://test.pypi.org/account/register/
- twineがインストールされていること: `pip install twine`

## 手順

### 1. TestPyPIアカウントの作成

1. https://test.pypi.org/account/register/ にアクセス
2. アカウントを作成（すでにある場合はログイン）

### 2. APIトークンの生成

1. TestPyPIにログイン
2. Account settings → API tokens へ移動
3. "Add API token" をクリック
4. Token name: `src-check-publish` （任意の名前）
5. Scope: `Entire account` を選択
6. "Add token" をクリック
7. 生成されたトークンをコピー（`pypi-` で始まる文字列）

### 3. 環境変数の設定

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmc...  # 生成されたトークンをここに貼り付け
```

### 4. TestPyPIへのアップロード

```bash
# 現在のディレクトリがプロジェクトルート（src-check/）であることを確認
pwd

# パッケージファイルの確認
ls -la dist/

# TestPyPIへアップロード
twine upload --repository testpypi dist/*
```

### 5. アップロード成功の確認

アップロードが成功すると、以下のURLでパッケージが確認できます：
https://test.pypi.org/project/src-check/0.2.0/

### 6. TestPyPIからのインストールテスト

```bash
# 新しい仮想環境を作成
python -m venv test-install-env
source test-install-env/bin/activate  # Windows: test-install-env\Scripts\activate

# TestPyPIからインストール
pip install -i https://test.pypi.org/simple/ src-check==0.2.0

# 動作確認
src-check --version
src-check --help
```

## トラブルシューティング

### 認証エラーが発生する場合

1. トークンが正しくコピーされているか確認
2. `__token__` という文字列を正確に使用しているか確認
3. トークンの前後に余分なスペースがないか確認

### パッケージ名が既に使用されている場合

他のユーザーが既に `src-check` という名前を使用している可能性があります。
その場合は、プロジェクト名を変更する必要があります。

## 次のステップ

TestPyPIでの動作確認が完了したら、本番のPyPIへの公開を行います。
手順は基本的に同じですが、以下の点が異なります：

1. https://pypi.org/ を使用
2. `--repository testpypi` オプションを削除
3. 本番用の新しいAPIトークンを生成

## 参考リンク

- TestPyPI: https://test.pypi.org/
- Packaging Python Projects: https://packaging.python.org/tutorials/packaging-projects/
- Using TestPyPI: https://packaging.python.org/guides/using-testpypi/