# Git Operations Module - Cresta Open Data

## 概要

このモジュールは、Cresta Open Dataリポジトリにおけるdetached HEAD状態からのブランチ切り替えが失敗する問題を修正するために開発されました。

## 問題の詳細

### 元の問題
```bash
[12:36:49] Git操作を開始します...
[12:36:49] 現在のブランチを確認中...
[12:36:49] detached HEAD状態を検出、mainブランチに切り替えます...
[12:36:49] ❌ ブランチ切り替えエラー: error: pathspec 'master' did not match any file(s) known to git
```

### 問題の原因
- `git checkout main` が失敗
- `git checkout master` も失敗  
- エラー: `error: pathspec 'main/master' did not match any file(s) known to git`

## 解決内容

### 実装した改善点

1. **動的ブランチ検出**
   - ローカルブランチとリモートブランチの両方を確認
   - 利用可能なブランチを自動検出

2. **優先順位ベースのブランチ選択**
   - `main` → `master` → `develop` の順で優先
   - 利用可能な最初のブランチを自動選択

3. **リモートブランチからの自動作成**
   - リモートにのみ存在するブランチをローカルに作成
   - `git fetch origin branch:branch` を使用

4. **新しいブランチの自動作成**
   - どのブランチも見つからない場合、新しいブランチを作成
   - デフォルトでは `main` ブランチを作成

5. **堅牢なエラーハンドリング**
   - 詳細なログ出力
   - タイムアウト制御
   - 適切なエラーメッセージ

## 使用方法

### 基本的な使用

```python
from git_operations import GitOperations

# インスタンス作成
git_ops = GitOperations()

# Git操作の実行（自動的にブランチ問題を解決）
success = git_ops.execute_git_push("コミットメッセージ")
```

### コマンドライン使用

```bash
# 基本的なGit操作
python3 git_operations.py --message "コミットメッセージ"

# 特定のファイルのみコミット
python3 git_operations.py --message "更新" --files file1.py file2.json

# ブランチ切り替えテスト
python3 git_operations.py --test-branch main
```

### テストの実行

```bash
# 全テストの実行
python3 test_git_operations.py
```

## 機能詳細

### 1. ブランチ検出機能

```python
def get_available_branches(self) -> Tuple[List[str], List[str]]:
    """利用可能なローカルブランチとリモートブランチを取得"""
```

- ローカルブランチ: `git branch --format=%(refname:short)`
- リモートブランチ: `git branch -r --format=%(refname:short)`

### 2. 自動ブランチ選択

```python
def find_best_branch(self) -> Optional[str]:
    """優先順位に基づいて最適なブランチを選択"""
```

優先順位:
1. `main`
2. `master` 
3. `develop`
4. 利用可能な最初のブランチ

### 3. ブランチ作成機能

```python
def ensure_branch_available(self, branch_name: str) -> bool:
    """ブランチが利用可能であることを確認し、必要に応じて作成"""
```

処理フロー:
1. ローカルブランチに存在チェック
2. リモートブランチに存在チェック → ローカルに作成
3. どちらにも存在しない → 新規作成

### 4. 改善されたGit操作

```python
def execute_git_push(self, message: str = None, files: List[str] = None) -> bool:
    """Gitプッシュ操作を実行（改善版）"""
```

処理フロー:
1. 現在のブランチ状態確認
2. detached HEAD検出時の自動修復
3. ファイルのステージング
4. コミット実行
5. アップストリーム設定付きプッシュ

## ログ出力例

### 正常なケース
```
[12:36:49] Git操作を開始します...
[12:36:49] 現在のブランチを確認中...
[12:36:49] detached HEAD状態を検出、適切なブランチに切り替えます...
[12:36:49] リモートブランチをフェッチ中...
[12:36:49] ✅ リモートブランチのフェッチが完了しました
[12:36:49] 優先ブランチ 'main' が見つかりました
[12:36:49] ブランチ 'main' はローカルに存在します
[12:36:49] ✅ ブランチ 'main' に正常に切り替えました
[12:36:49] ✅ コミットが完了しました: テストコミット
[12:36:49] ✅ プッシュが完了しました: main
```

### ブランチ作成ケース
```
[12:36:49] ブランチ 'main' が見つかりません。新しく作成します
[12:36:49] 新しいブランチ 'main' を作成中...
[12:36:49] ✅ 新しいブランチ 'main' を正常に作成しました
```

## エラーハンドリング

### タイムアウト制御
- Git操作は30秒でタイムアウト
- 長時間実行されるコマンドを防止

### 認証エラー
- GitHub認証失敗時の適切なエラーメッセージ
- プッシュ権限がない場合の処理

### ネットワークエラー
- リモートアクセス失敗時のフォールバック
- ローカル操作のみで継続

## 技術仕様

### 依存関係
- Python 3.6+
- Git 2.0+
- subprocess (標準ライブラリ)
- logging (標準ライブラリ)

### 対応Git操作
- `git fetch`
- `git branch`
- `git checkout`
- `git add`
- `git commit`
- `git push`

### ファイル構成
```
git_operations.py      # メインモジュール
test_git_operations.py # テストスイート
README_git_ops.md      # このドキュメント
```

## 今後の改善予定

1. **設定ファイル対応**
   - ブランチ優先順位のカスタマイズ
   - タイムアウト時間の設定

2. **マルチリモート対応**
   - 複数のリモートリポジトリサポート
   - リモート別の認証設定

3. **詳細な統計情報**
   - 操作時間の計測
   - 成功/失敗率の記録

4. **GUI対応**
   - Web インターフェース
   - 進行状況の可視化