# CI/CD統合ガイド

src-checkを継続的インテグレーション（CI）および継続的デリバリー（CD）パイプラインに統合する方法を説明します。

## 📋 目次

- [GitHub Actions](#github-actions)
- [GitLab CI](#gitlab-ci)
- [pre-commitフック](#pre-commitフック)
- [Jenkins](#jenkins)
- [CircleCI](#circleci)
- [その他のCIツール](#その他のciツール)

## GitHub Actions

### 基本的な設定

`.github/workflows/code-quality.yml`を作成：

```yaml
name: Code Quality Check

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  src-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install src-check
      run: |
        pip install --upgrade pip
        pip install src-check
    
    - name: Run src-check
      run: |
        src-check --format github
    
    - name: Upload results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: src-check-results
        path: src-check-report.json
```

### プルリクエストでのチェック

```yaml
name: PR Quality Gate

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0  # Full history for better analysis
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install src-check
    
    - name: Run quality checks
      id: quality
      run: |
        src-check-kpi --format json > kpi-scores.json
        echo "kpi_score=$(jq .total_score kpi-scores.json)" >> $GITHUB_OUTPUT
    
    - name: Comment PR
      uses: actions/github-script@v6
      if: github.event_name == 'pull_request'
      with:
        script: |
          const score = ${{ steps.quality.outputs.kpi_score }};
          const emoji = score >= 80 ? '✅' : score >= 60 ? '⚠️' : '❌';
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: `## ${emoji} Code Quality Score: ${score}/100\n\nRun \`src-check\` locally for detailed results.`
          })
```

### バッジの追加

README.mdに追加：

```markdown
![Code Quality](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Code%20Quality%20Check/badge.svg)
```

## GitLab CI

`.gitlab-ci.yml`を作成：

```yaml
stages:
  - test
  - quality

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip

code-quality:
  stage: quality
  image: python:3.11
  before_script:
    - pip install --upgrade pip
    - pip install src-check
  script:
    - src-check --format gitlab > code-quality-report.json
  artifacts:
    reports:
      codequality: code-quality-report.json
    expire_in: 1 week
  only:
    - merge_requests
    - main
    - develop

kpi-score:
  stage: quality
  image: python:3.11
  before_script:
    - pip install src-check
  script:
    - src-check-kpi --format json
    - |
      score=$(src-check-kpi --format json | jq -r .total_score)
      if [ "$score" -lt 60 ]; then
        echo "❌ KPI score is too low: $score/100"
        exit 1
      fi
  only:
    - merge_requests
```

## pre-commitフック

### 設定ファイル

`.pre-commit-config.yaml`を作成：

```yaml
repos:
  - repo: https://github.com/sugipamo/src-check
    rev: v0.2.0
    hooks:
      - id: src-check
        name: src-check
        entry: src-check
        language: system
        types: [python]
        require_serial: true
        verbose: true

  - repo: local
    hooks:
      - id: src-check-kpi
        name: Check KPI Score
        entry: bash -c 'score=$(src-check-kpi --format json | jq -r .total_score); if [ "$score" -lt 70 ]; then echo "KPI score too low: $score"; exit 1; fi'
        language: system
        always_run: true
        pass_filenames: false
```

### インストールと使用

```bash
# pre-commitのインストール
pip install pre-commit

# フックの設定
pre-commit install

# 手動実行
pre-commit run --all-files
```

## Jenkins

`Jenkinsfile`の例：

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install src-check
                '''
            }
        }
        
        stage('Code Quality Check') {
            steps {
                sh '''
                    . venv/bin/activate
                    src-check --format jenkins > src-check-report.xml
                '''
            }
            post {
                always {
                    junit 'src-check-report.xml'
                }
            }
        }
        
        stage('KPI Score') {
            steps {
                sh '''
                    . venv/bin/activate
                    src-check-kpi --format json > kpi-score.json
                '''
                
                script {
                    def kpiData = readJSON file: 'kpi-score.json'
                    if (kpiData.total_score < 70) {
                        error("KPI score too low: ${kpiData.total_score}/100")
                    }
                }
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'src-check-report.xml,kpi-score.json', 
                             allowEmptyArchive: true
        }
    }
}
```

## CircleCI

`.circleci/config.yml`の例：

```yaml
version: 2.1

jobs:
  code-quality:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      
      - restore_cache:
          keys:
            - v1-dependencies-{{ checksum "requirements.txt" }}
            - v1-dependencies-
      
      - run:
          name: Install dependencies
          command: |
            python -m venv venv
            . venv/bin/activate
            pip install --upgrade pip
            pip install src-check
      
      - save_cache:
          paths:
            - ./venv
          key: v1-dependencies-{{ checksum "requirements.txt" }}
      
      - run:
          name: Run src-check
          command: |
            . venv/bin/activate
            src-check --format json > test-results/src-check.json
      
      - run:
          name: Check KPI Score
          command: |
            . venv/bin/activate
            score=$(src-check-kpi --format json | jq -r .total_score)
            echo "KPI Score: $score/100"
            if [ "$score" -lt 70 ]; then
              echo "KPI score is too low!"
              exit 1
            fi
      
      - store_test_results:
          path: test-results
      
      - store_artifacts:
          path: test-results

workflows:
  version: 2
  quality:
    jobs:
      - code-quality
```

## その他のCIツール

### Azure DevOps

`azure-pipelines.yml`の例：

```yaml
trigger:
- main
- develop

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'
    
- script: |
    pip install --upgrade pip
    pip install src-check
  displayName: 'Install dependencies'
  
- script: |
    src-check --format json > $(Build.ArtifactStagingDirectory)/src-check-report.json
  displayName: 'Run src-check'
  
- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: '$(Build.ArtifactStagingDirectory)'
    artifactName: 'quality-reports'
```

### Bitbucket Pipelines

`bitbucket-pipelines.yml`の例：

```yaml
pipelines:
  default:
    - step:
        name: Code Quality Check
        image: python:3.11
        caches:
          - pip
        script:
          - pip install src-check
          - src-check --format json > src-check-report.json
          - |
            score=$(src-check-kpi --format json | jq -r .total_score)
            if [ "$score" -lt 70 ]; then
              echo "KPI score too low: $score"
              exit 1
            fi
        artifacts:
          - src-check-report.json
```

## ベストプラクティス

### 1. 段階的な導入

最初は警告のみ、徐々に必須チェックに：

```yaml
# 第1段階: 警告のみ
- run: src-check || true

# 第2段階: 特定のチェッカーのみ必須
- run: src-check --checkers security,license

# 第3段階: KPIスコアで判定
- run: |
    score=$(src-check-kpi --format json | jq -r .total_score)
    if [ "$score" -lt 60 ]; then exit 1; fi
```

### 2. キャッシュの活用

依存関係のキャッシュで高速化：

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### 3. 並列実行

大規模プロジェクトでは並列実行を検討：

```bash
# ディレクトリごとに並列実行
src-check src/module1 &
src-check src/module2 &
src-check src/module3 &
wait
```

### 4. レポートの保存

長期的な品質トレンドの追跡：

```bash
# 日付付きでレポートを保存
src-check-kpi --format json > reports/kpi-$(date +%Y%m%d).json
```

### 5. 通知の設定

品質低下時の通知：

```yaml
- name: Notify on quality degradation
  if: failure()
  run: |
    curl -X POST $SLACK_WEBHOOK_URL \
      -H 'Content-type: application/json' \
      -d '{"text":"⚠️ Code quality check failed!"}'
```

## トラブルシューティング

### 問題: CIでのみ失敗する

ローカルと同じPythonバージョンを使用：

```yaml
- uses: actions/setup-python@v4
  with:
    python-version-file: '.python-version'
```

### 問題: タイムアウト

タイムアウト値を調整：

```yaml
- run: src-check
  timeout-minutes: 10
```

### 問題: メモリ不足

並列度を制限：

```bash
export SRC_CHECK_WORKERS=2
src-check
```