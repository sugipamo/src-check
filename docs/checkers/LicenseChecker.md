# LicenseChecker

## 概要と目的

LicenseCheckerは、プロジェクトのライセンスコンプライアンスと一貫性を検証するチェッカーです。プロジェクトのライセンスファイルの存在、依存関係のライセンス互換性、著作権表示の確認などを行い、法的リスクを最小化します。

## 検出される問題（エラーコード）

### LIC001 - LICENSEファイルの欠如
- プロジェクトルートにLICENSEファイルが存在しない
- 重要度: HIGH

### LIC002 - 認識できないライセンス形式
- LICENSEファイルの内容が標準的なライセンスと一致しない
- 重要度: MEDIUM

### LIC003 - ライセンス互換性の問題
- 依存関係のライセンスがプロジェクトのライセンスと互換性がない
- 重要度: HIGH

### LIC004 - コピーレフトライセンスの検出
- GPL、LGPL、MPLなどのコピーレフトライセンスを持つ依存関係
- 重要度: MEDIUM

### LIC005 - 著作権ヘッダーの欠如
- ソースファイルに著作権表示がない
- 重要度: LOW

### LIC006 - 古い著作権年
- 著作権年が5年以上前
- 重要度: INFO

### LIC007 - ライセンスの不一致
- LICENSEファイルとpyproject.tomlのライセンス情報が異なる
- 重要度: HIGH

### LIC008 - ライセンス情報のない依存関係
- 依存パッケージにライセンス情報がない
- 重要度: LOW

## 設定オプション

現在、LicenseCheckerには設定可能なオプションはありません。以下のライセンスを自動認識します：
- MIT
- Apache-2.0
- GPL-3.0/GPL-2.0
- BSD-3-Clause/BSD-2-Clause
- ISC
- LGPL-3.0/LGPL-2.1
- MPL-2.0
- Unlicense

## 検出される問題の例

### LICENSEファイルの欠如
```
プロジェクトルート/
├── src/
├── tests/
├── README.md
└── pyproject.toml
# LICENSEファイルがない！
```

### ライセンスの不一致
```toml
# pyproject.toml
[project]
name = "myproject"
license = {text = "Apache-2.0"}

# LICENSE ファイル
MIT License
Copyright (c) 2024 ...
```

### コピーレフトライセンスの依存
```txt
# pip list の出力
Package         License
--------        -------
requests        Apache-2.0
flask           BSD-3-Clause
some-gpl-lib    GPL-3.0    # コピーレフト！
```

### 著作権ヘッダーの欠如
```python
# 悪い例 - module.py
import os
import sys

def main():
    pass

# 良い例 - module.py
# Copyright (c) 2024 Your Name/Organization
# Licensed under the MIT License
# See LICENSE file for details

import os
import sys

def main():
    pass
```

## 一般的な問題の修正方法

### 1. LICENSEファイルの作成
```markdown
# MIT License の例
MIT License

Copyright (c) 2024 [あなたの名前/組織名]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 2. pyproject.tomlでのライセンス指定
```toml
[project]
name = "myproject"
version = "1.0.0"
description = "My awesome project"
authors = [{name = "Your Name", email = "you@example.com"}]
license = {text = "MIT"}  # または {file = "LICENSE"}

# クラシファイアーでも指定
classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
]
```

### 3. 著作権ヘッダーの追加
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024 Your Name/Organization
#
# This file is part of [Project Name]
#
# Licensed under the MIT License.
# You may obtain a copy of the License at
#
#     https://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""モジュールの説明"""

import os
# ... rest of the code
```

### 4. 依存関係のライセンス確認
```python
# check_licenses.py
import pkg_resources

def check_dependency_licenses():
    """インストール済みパッケージのライセンスを確認"""
    licenses = {}
    for pkg in pkg_resources.working_set:
        try:
            metadata = pkg.get_metadata_lines('METADATA')
            for line in metadata:
                if line.startswith('License:'):
                    licenses[pkg.key] = line.split(':', 1)[1].strip()
                    break
        except:
            licenses[pkg.key] = "Unknown"
    
    # コピーレフトライセンスの確認
    copyleft = ['GPL', 'LGPL', 'AGPL', 'MPL']
    problematic = {pkg: lic for pkg, lic in licenses.items() 
                   if any(cl in lic for cl in copyleft)}
    
    if problematic:
        print("コピーレフトライセンスの依存関係:")
        for pkg, lic in problematic.items():
            print(f"  {pkg}: {lic}")
    
    return licenses

# pip-licenses ツールの使用
# pip install pip-licenses
# pip-licenses --format=markdown
```

### 5. ライセンス互換性マトリックス
```python
# ライセンス互換性の確認
COMPATIBILITY = {
    'MIT': ['MIT', 'BSD', 'Apache-2.0', 'ISC'],
    'BSD': ['MIT', 'BSD', 'Apache-2.0', 'ISC'],
    'Apache-2.0': ['MIT', 'BSD', 'Apache-2.0', 'ISC'],
    'GPL-3.0': ['GPL-3.0', 'LGPL-3.0'],
    'LGPL-3.0': ['MIT', 'BSD', 'Apache-2.0', 'LGPL-3.0', 'GPL-3.0'],
}

def check_compatibility(project_license, dependency_license):
    """ライセンスの互換性をチェック"""
    if project_license not in COMPATIBILITY:
        return False
    
    compatible_licenses = COMPATIBILITY[project_license]
    return any(compat in dependency_license for compat in compatible_licenses)
```

## ベストプラクティス

1. **明示的なライセンス選択**: プロジェクト開始時にライセンスを決定
2. **ライセンスファイルの配置**: 必ずプロジェクトルートにLICENSEファイルを配置
3. **一貫性の維持**: README、pyproject.toml、LICENSEファイルで同じライセンス情報
4. **依存関係の監査**: 新しい依存関係を追加する前にライセンスを確認
5. **著作権表示の更新**: 年次で著作権年を更新
6. **ライセンスヘッダーテンプレート**: プロジェクトで統一されたヘッダーを使用
7. **CI/CDでの自動チェック**: ライセンスコンプライアンスを自動的に検証