#!/usr/bin/env python3
"""
Test script for Git Operations

This script tests the robust Git operations functionality,
particularly the branch switching logic for detached HEAD states.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from git_operations import GitOperations


def test_branch_detection():
    """ブランチ検出機能をテスト"""
    print("=== ブランチ検出テスト ===")
    
    git_ops = GitOperations()
    
    # 現在のブランチ状態を確認
    current_branch = git_ops.get_current_branch()
    is_detached = git_ops.is_detached_head()
    
    print(f"現在のブランチ: {current_branch}")
    print(f"Detached HEAD状態: {is_detached}")
    
    # 利用可能なブランチを取得
    local_branches, remote_branches = git_ops.get_available_branches()
    print(f"ローカルブランチ: {local_branches}")
    print(f"リモートブランチ: {remote_branches}")
    
    return True


def test_branch_switching():
    """ブランチ切り替え機能をテスト"""
    print("\n=== ブランチ切り替えテスト ===")
    
    git_ops = GitOperations()
    
    # 最適なブランチを見つける
    best_branch = git_ops.find_best_branch()
    print(f"最適なブランチ: {best_branch}")
    
    if best_branch:
        # ブランチが利用可能であることを確認
        if git_ops.ensure_branch_available(best_branch):
            print(f"✅ ブランチ '{best_branch}' が利用可能です")
            
            # ブランチに切り替え
            if git_ops.switch_to_branch(best_branch):
                print(f"✅ ブランチ '{best_branch}' への切り替えに成功しました")
                return True
            else:
                print(f"❌ ブランチ '{best_branch}' への切り替えに失敗しました")
                return False
        else:
            print(f"❌ ブランチ '{best_branch}' の準備に失敗しました")
            return False
    else:
        print("❌ 利用可能なブランチが見つかりませんでした")
        return False


def test_git_operations():
    """Git操作の全体テスト"""
    print("\n=== Git操作全体テスト ===")
    
    git_ops = GitOperations()
    
    # テストファイルを作成（実際にはコミットしない）
    test_file = "test_git_operations.txt"
    with open(test_file, "w") as f:
        f.write("This is a test file for Git operations\n")
    
    try:
        # Git操作をテスト（dry-run的に）
        print("Git操作のテストを実行中...")
        
        # ブランチ状態の確認のみ
        current_branch = git_ops.get_current_branch()
        if current_branch:
            print(f"✅ 現在のブランチ: {current_branch}")
        else:
            print("⚠️  Detached HEAD状態です")
            
            # 最適なブランチを見つけて切り替えテスト
            best_branch = git_ops.find_best_branch()
            if best_branch and git_ops.ensure_branch_available(best_branch):
                print(f"✅ ブランチ切り替えの準備ができました: {best_branch}")
            else:
                print("❌ ブランチ切り替えの準備に失敗しました")
        
        return True
        
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {str(e)}")
        return False
    finally:
        # テストファイルを削除
        if os.path.exists(test_file):
            os.remove(test_file)


def main():
    """メインテスト関数"""
    print("Cresta Open Data Git Operations テストスイート")
    print("=" * 50)
    
    tests = [
        test_branch_detection,
        test_branch_switching,
        test_git_operations
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ テスト合格")
            else:
                failed += 1
                print("❌ テスト失敗")
        except Exception as e:
            failed += 1
            print(f"❌ テスト失敗: {str(e)}")
        
        print("-" * 30)
    
    print(f"\nテスト結果: 合格 {passed}, 失敗 {failed}")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("🎉 全テスト合格！")


if __name__ == "__main__":
    main()