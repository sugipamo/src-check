# TestQualityChecker

## 概要と目的

TestQualityCheckerは、テストコードの品質とカバレッジの問題を検出するチェッカーです。テストの構造、アサーション、命名規則、およびテストされていない関数の検出を行い、信頼性の高いテストスイートの構築を支援します。

## 検出される問題（エラーコード）

### テストファイルの問題
- 空のテスト関数
- ドキュメント文字列がないテスト関数
- 長すぎるテスト関数（50行超）
- アサーションがないテスト
- アサーションが多すぎるテスト（10個超）
- 汎用的なテスト名（test1、test_など）
- 重要度: MEDIUM

### 非テストファイルの問題
- 3つ以上の公開関数があるがテストがない可能性
- 重要度: MEDIUM

## 設定オプション

現在、以下の設定がハードコードされています：
- テスト関数の最大行数: 50行
- テスト関数あたりの最大アサーション数: 10個
- テスト推奨の公開関数数: 3個以上

## 検出される問題の例

### 空のテスト関数
```python
# 悪い例
def test_user_creation():
    pass  # 空のテスト

def test_validation():
    # TODOコメントだけ
    # TODO: implement this test
    pass
```

### ドキュメント文字列の欠如
```python
# 悪い例
def test_calculate_total():
    result = calculate_total([1, 2, 3])
    assert result == 6

# 良い例
def test_calculate_total():
    """calculate_total関数が正しく合計を計算することを確認する"""
    result = calculate_total([1, 2, 3])
    assert result == 6
```

### アサーションの問題
```python
# 悪い例 - アサーションなし
def test_process_data():
    data = [1, 2, 3]
    result = process_data(data)
    # アサーションがない！

# 悪い例 - 無意味なアサーション
def test_always_true():
    assert True  # 常に成功する

# 悪い例 - 多すぎるアサーション
def test_user_model():
    user = User("John", "john@example.com")
    assert user.name == "John"
    assert user.email == "john@example.com"
    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None
    # ... 10個以上のアサーション
```

### 汎用的なテスト名
```python
# 悪い例
def test1():
    pass

def test_():
    pass

def test_a():
    pass

class Test:  # 汎用的なクラス名
    pass

# 良い例
def test_user_can_login_with_valid_credentials():
    pass

def test_invalid_email_raises_validation_error():
    pass

class TestUserAuthentication:
    pass
```

## 一般的な問題の修正方法

### 1. 明確で簡潔なテストの作成
```python
# 良い例 - Arrange-Act-Assert パターン
def test_calculate_discount_applies_10_percent_for_premium_users():
    """プレミアムユーザーに10%の割引が適用されることを確認する"""
    # Arrange
    user = User(type="premium")
    original_price = 100
    
    # Act
    discounted_price = calculate_discount(user, original_price)
    
    # Assert
    assert discounted_price == 90
```

### 2. 適切なテスト分割
```python
# 良い例 - 1つのテストで1つのことを検証
def test_user_creation_sets_default_values():
    """ユーザー作成時にデフォルト値が設定されることを確認"""
    user = User("John")
    
    assert user.is_active is True
    assert user.role == "user"

def test_user_creation_generates_unique_id():
    """ユーザー作成時にユニークIDが生成されることを確認"""
    user1 = User("John")
    user2 = User("Jane")
    
    assert user1.id != user2.id
    assert user1.id is not None
```

### 3. パラメータ化テストの活用
```python
# 良い例 - pytestのパラメータ化
import pytest

@pytest.mark.parametrize("input_value, expected", [
    (0, 0),
    (1, 1),
    (-1, 1),
    (10, 100),
])
def test_square_function(input_value, expected):
    """square関数が正しく二乗を計算することを確認"""
    assert square(input_value) == expected
```

### 4. テストのドキュメント化
```python
# 良い例
class TestUserRegistration:
    """ユーザー登録機能のテストスイート"""
    
    def test_valid_registration_creates_user(self):
        """有効なデータでユーザー登録が成功することを確認
        
        Given: 有効なメールアドレスとパスワード
        When: register_user()を呼び出す
        Then: 新しいユーザーが作成され、確認メールが送信される
        """
        # テスト実装
        pass
    
    def test_duplicate_email_raises_error(self):
        """重複するメールアドレスでエラーが発生することを確認"""
        # テスト実装
        pass
```

### 5. モックとフィクスチャの活用
```python
# 良い例
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def user():
    """テスト用ユーザーフィクスチャ"""
    return User("test@example.com", "password123")

def test_send_welcome_email(user):
    """ウェルカムメールが送信されることを確認"""
    with patch('email_service.send') as mock_send:
        send_welcome_email(user)
        
        mock_send.assert_called_once_with(
            to=user.email,
            subject="Welcome!",
            body=Mock.ANY
        )
```

## ベストプラクティス

1. **テスト駆動開発（TDD）**: テストを先に書く
2. **AAA パターン**: Arrange（準備）、Act（実行）、Assert（検証）
3. **1テスト1アサーション原則**: 複数の観点を検証する場合は別のテストに分割
4. **説明的なテスト名**: `test_<何を>_<条件>_<期待結果>`
5. **独立性**: テストは他のテストに依存しない
6. **再現性**: 同じテストは何度実行しても同じ結果
7. **高速性**: 単体テストは高速に実行される
8. **カバレッジ**: 重要なビジネスロジックは100%カバー