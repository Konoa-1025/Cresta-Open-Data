#!/usr/bin/env python3
"""
Git Operations Module for Cresta Open Data

This module provides robust Git operations with improved branch switching logic
to handle detached HEAD states and branch availability issues.

Author: Cresta Development Team
Date: 2025-08-16
"""

import subprocess
import sys
import logging
from datetime import datetime
from typing import List, Optional, Tuple


class GitOperations:
    """Git操作を管理するクラス"""
    
    def __init__(self, repo_path: str = "."):
        """
        GitOperations初期化
        
        Args:
            repo_path (str): Gitリポジトリのパス
        """
        self.repo_path = repo_path
        self.setup_logging()
        
    def setup_logging(self):
        """ログ設定を初期化"""
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
    def run_git_command(self, command: List[str], capture_output: bool = True) -> Tuple[bool, str]:
        """
        Gitコマンドを実行
        
        Args:
            command (List[str]): 実行するGitコマンド
            capture_output (bool): 出力をキャプチャするかどうか
            
        Returns:
            Tuple[bool, str]: (成功/失敗, 出力/エラーメッセージ)
        """
        try:
            full_command = ["git", "--no-pager"] + command
            result = subprocess.run(
                full_command,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()
                
        except subprocess.TimeoutExpired:
            return False, "Git command timed out"
        except Exception as e:
            return False, f"Git command failed: {str(e)}"
    
    def get_current_branch(self) -> Optional[str]:
        """
        現在のブランチ名を取得
        
        Returns:
            Optional[str]: ブランチ名、detached HEADの場合はNone
        """
        success, output = self.run_git_command(["branch", "--show-current"])
        if success and output:
            return output
        return None
    
    def is_detached_head(self) -> bool:
        """
        detached HEAD状態かどうかを確認
        
        Returns:
            bool: detached HEAD状態の場合True
        """
        return self.get_current_branch() is None
    
    def get_available_branches(self) -> Tuple[List[str], List[str]]:
        """
        利用可能なローカルブランチとリモートブランチを取得
        
        Returns:
            Tuple[List[str], List[str]]: (ローカルブランチ, リモートブランチ)
        """
        # ローカルブランチを取得
        local_success, local_output = self.run_git_command(["branch", "--format=%(refname:short)"])
        local_branches = []
        if local_success:
            local_branches = [branch.strip() for branch in local_output.split('\n') if branch.strip()]
        
        # リモートブランチを取得
        remote_success, remote_output = self.run_git_command(["branch", "-r", "--format=%(refname:short)"])
        remote_branches = []
        if remote_success:
            remote_branches = [
                branch.strip().replace('origin/', '') 
                for branch in remote_output.split('\n') 
                if branch.strip() and not branch.strip().endswith('/HEAD')
            ]
        
        self.logger.info(f"ローカルブランチ: {local_branches}")
        self.logger.info(f"リモートブランチ: {remote_branches}")
        
        return local_branches, remote_branches
    
    def fetch_remote_branches(self) -> bool:
        """
        リモートブランチをフェッチ
        
        Returns:
            bool: フェッチ成功の場合True
        """
        self.logger.info("リモートブランチをフェッチ中...")
        success, output = self.run_git_command(["fetch", "origin"])
        if success:
            self.logger.info("✅ リモートブランチのフェッチが完了しました")
            return True
        else:
            self.logger.error(f"❌ リモートブランチのフェッチに失敗しました: {output}")
            return False
    
    def create_branch_from_remote(self, branch_name: str) -> bool:
        """
        リモートブランチからローカルブランチを作成
        
        Args:
            branch_name (str): 作成するブランチ名
            
        Returns:
            bool: 作成成功の場合True
        """
        self.logger.info(f"リモートブランチ origin/{branch_name} からローカルブランチを作成中...")
        success, output = self.run_git_command(["fetch", "origin", f"{branch_name}:{branch_name}"])
        if success:
            self.logger.info(f"✅ ブランチ '{branch_name}' を正常に作成しました")
            return True
        else:
            self.logger.error(f"❌ ブランチ '{branch_name}' の作成に失敗しました: {output}")
            return False
    
    def create_new_branch(self, branch_name: str, base_branch: str = None) -> bool:
        """
        新しいブランチを作成
        
        Args:
            branch_name (str): 作成するブランチ名
            base_branch (str): ベースとなるブランチ名（省略時は現在のHEAD）
            
        Returns:
            bool: 作成成功の場合True
        """
        command = ["checkout", "-b", branch_name]
        if base_branch:
            command.append(base_branch)
            
        self.logger.info(f"新しいブランチ '{branch_name}' を作成中...")
        success, output = self.run_git_command(command)
        if success:
            self.logger.info(f"✅ 新しいブランチ '{branch_name}' を正常に作成しました")
            return True
        else:
            self.logger.error(f"❌ ブランチ '{branch_name}' の作成に失敗しました: {output}")
            return False
    
    def switch_to_branch(self, branch_name: str) -> bool:
        """
        指定されたブランチに切り替え
        
        Args:
            branch_name (str): 切り替え先のブランチ名
            
        Returns:
            bool: 切り替え成功の場合True
        """
        self.logger.info(f"ブランチ '{branch_name}' に切り替え中...")
        success, output = self.run_git_command(["checkout", branch_name])
        if success:
            self.logger.info(f"✅ ブランチ '{branch_name}' に正常に切り替えました")
            return True
        else:
            self.logger.error(f"❌ ブランチ '{branch_name}' への切り替えに失敗しました: {output}")
            return False
    
    def find_best_branch(self) -> Optional[str]:
        """
        優先順位に基づいて最適なブランチを選択
        
        Returns:
            Optional[str]: 選択されたブランチ名
        """
        # 優先順位: main → master → develop
        priority_branches = ["main", "master", "develop"]
        
        # リモートブランチをフェッチ
        self.fetch_remote_branches()
        
        # 利用可能なブランチを取得
        local_branches, remote_branches = self.get_available_branches()
        all_available_branches = list(set(local_branches + remote_branches))
        
        # 優先順位に従ってブランチを選択
        for preferred_branch in priority_branches:
            if preferred_branch in all_available_branches:
                self.logger.info(f"優先ブランチ '{preferred_branch}' が見つかりました")
                return preferred_branch
        
        # 優先ブランチが見つからない場合、利用可能な最初のブランチを選択
        if all_available_branches:
            selected_branch = all_available_branches[0]
            self.logger.info(f"利用可能なブランチ '{selected_branch}' を選択しました")
            return selected_branch
        
        self.logger.warning("利用可能なブランチが見つかりませんでした")
        return None
    
    def ensure_branch_available(self, branch_name: str) -> bool:
        """
        ブランチが利用可能であることを確認し、必要に応じて作成
        
        Args:
            branch_name (str): 確認するブランチ名
            
        Returns:
            bool: ブランチが利用可能な場合True
        """
        local_branches, remote_branches = self.get_available_branches()
        
        # ローカルブランチに存在する場合
        if branch_name in local_branches:
            self.logger.info(f"ブランチ '{branch_name}' はローカルに存在します")
            return True
        
        # リモートブランチに存在する場合、ローカルに作成
        if branch_name in remote_branches:
            self.logger.info(f"ブランチ '{branch_name}' はリモートに存在します")
            return self.create_branch_from_remote(branch_name)
        
        # どちらにも存在しない場合、新しく作成
        self.logger.info(f"ブランチ '{branch_name}' が見つかりません。新しく作成します")
        return self.create_new_branch(branch_name)
    
    def execute_git_push(self, message: str = None, files: List[str] = None) -> bool:
        """
        Gitプッシュ操作を実行（改善版）
        
        Args:
            message (str): コミットメッセージ
            files (List[str]): コミット対象のファイル（省略時は全ファイル）
            
        Returns:
            bool: プッシュ成功の場合True
        """
        self.logger.info("Git操作を開始します...")
        
        try:
            # 現在のブランチを確認
            self.logger.info("現在のブランチを確認中...")
            current_branch = self.get_current_branch()
            
            if current_branch:
                self.logger.info(f"現在のブランチ: {current_branch}")
            else:
                self.logger.info("detached HEAD状態を検出、適切なブランチに切り替えます...")
                
                # 最適なブランチを見つけて切り替え
                target_branch = self.find_best_branch()
                if not target_branch:
                    # どのブランチも見つからない場合、mainブランチを新規作成
                    target_branch = "main"
                    self.logger.info(f"デフォルトブランチ '{target_branch}' を作成します")
                    if not self.create_new_branch(target_branch):
                        return False
                else:
                    # ブランチが利用可能であることを確認
                    if not self.ensure_branch_available(target_branch):
                        return False
                    
                    # ブランチに切り替え
                    if not self.switch_to_branch(target_branch):
                        return False
                
                current_branch = target_branch
            
            # ファイルをステージング
            if files:
                for file in files:
                    success, output = self.run_git_command(["add", file])
                    if not success:
                        self.logger.error(f"❌ ファイル '{file}' のステージングに失敗しました: {output}")
                        return False
            else:
                success, output = self.run_git_command(["add", "."])
                if not success:
                    self.logger.error(f"❌ ファイルのステージングに失敗しました: {output}")
                    return False
            
            # 変更があるかチェック
            success, output = self.run_git_command(["diff", "--cached", "--quiet"])
            if success:  # 変更がない場合
                self.logger.info("コミットする変更がありません")
                return True
            
            # コミット
            commit_message = message or f"自動コミット {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            success, output = self.run_git_command(["commit", "-m", commit_message])
            if not success:
                self.logger.error(f"❌ コミットに失敗しました: {output}")
                return False
            
            self.logger.info(f"✅ コミットが完了しました: {commit_message}")
            
            # プッシュ
            self.logger.info(f"ブランチ '{current_branch}' をプッシュ中...")
            success, output = self.run_git_command(["push", "origin", current_branch])
            if not success:
                # アップストリームが設定されていない場合、設定してプッシュ
                self.logger.info("アップストリームを設定してプッシュを再試行中...")
                success, output = self.run_git_command(["push", "-u", "origin", current_branch])
                
            if success:
                self.logger.info(f"✅ プッシュが完了しました: {current_branch}")
                return True
            else:
                self.logger.error(f"❌ プッシュに失敗しました: {output}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Git操作中にエラーが発生しました: {str(e)}")
            return False


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cresta Open Data Git Operations')
    parser.add_argument('--message', '-m', help='コミットメッセージ')
    parser.add_argument('--files', '-f', nargs='*', help='コミット対象のファイル')
    parser.add_argument('--test-branch', '-t', help='ブランチ切り替えテスト')
    
    args = parser.parse_args()
    
    git_ops = GitOperations()
    
    if args.test_branch:
        # ブランチ切り替えテスト
        print(f"ブランチ '{args.test_branch}' への切り替えをテスト中...")
        if git_ops.ensure_branch_available(args.test_branch):
            success = git_ops.switch_to_branch(args.test_branch)
            if success:
                print(f"✅ ブランチ '{args.test_branch}' への切り替えに成功しました")
            else:
                print(f"❌ ブランチ '{args.test_branch}' への切り替えに失敗しました")
                sys.exit(1)
        else:
            print(f"❌ ブランチ '{args.test_branch}' の準備に失敗しました")
            sys.exit(1)
    else:
        # Git プッシュ操作
        success = git_ops.execute_git_push(args.message, args.files)
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()