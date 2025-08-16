#!/usr/bin/env python3
"""
Git utility functions for handling branch operations and push operations.
Specifically designed to handle detached HEAD state and dynamic branch detection.
"""

import subprocess
import sys
import os
from typing import List, Optional, Tuple


def run_git_command(command: List[str], cwd: str = None) -> Tuple[bool, str]:
    """
    Execute a git command and return success status and output.
    
    Args:
        command: List of command parts (e.g., ['git', 'branch', '-a'])
        cwd: Working directory for the command
        
    Returns:
        Tuple of (success: bool, output: str)
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0, result.stdout.strip() + result.stderr.strip()
    except Exception as e:
        return False, str(e)


def get_available_branches() -> List[str]:
    """
    Get all available branches (local and remote).
    
    Returns:
        List of branch names
    """
    branches = []
    
    # Get local branches
    success, output = run_git_command(['git', 'branch'])
    if success:
        for line in output.split('\n'):
            line = line.strip()
            if line and not line.startswith('*'):
                branches.append(line)
            elif line.startswith('* '):
                # Current branch (remove the * prefix)
                branch_name = line[2:].strip()
                if not branch_name.startswith('('):  # Ignore detached HEAD notation
                    branches.append(branch_name)
    
    # Get remote branches
    success, output = run_git_command(['git', 'branch', '-r'])
    if success:
        for line in output.split('\n'):
            line = line.strip()
            if line and not line.startswith('origin/HEAD'):
                # Remove 'origin/' prefix
                if line.startswith('origin/'):
                    branch_name = line[7:]  # Remove 'origin/' prefix
                    if branch_name not in branches:
                        branches.append(branch_name)
    
    return list(set(branches))


def is_detached_head() -> bool:
    """
    Check if we are in detached HEAD state.
    
    Returns:
        True if in detached HEAD state, False otherwise
    """
    success, output = run_git_command(['git', 'branch'])
    if success:
        for line in output.split('\n'):
            if line.strip().startswith('* (HEAD detached'):
                return True
    return False


def get_default_branch() -> Optional[str]:
    """
    Get the default branch name by checking common conventions and remote info.
    
    Returns:
        Branch name or None if not found
    """
    # First try to get the default branch from remote
    success, output = run_git_command(['git', 'symbolic-ref', 'refs/remotes/origin/HEAD'])
    if success and 'refs/remotes/origin/' in output:
        return output.split('refs/remotes/origin/')[-1].strip()
    
    # Fallback: check available branches for common default names
    available_branches = get_available_branches()
    
    # Priority order for default branch names
    default_candidates = ['main', 'master', 'develop', 'development']
    
    for candidate in default_candidates:
        if candidate in available_branches:
            return candidate
    
    # If no common default found, return the first available branch
    if available_branches:
        return available_branches[0]
    
    return None


def create_branch_from_remote(branch_name: str) -> bool:
    """
    Create a local branch tracking a remote branch.
    
    Args:
        branch_name: Name of the branch to create
        
    Returns:
        True if successful, False otherwise
    """
    # Check if remote branch exists
    success, _ = run_git_command(['git', 'show-ref', '--verify', '--quiet', f'refs/remotes/origin/{branch_name}'])
    
    if success:
        # Create local branch tracking the remote
        success, output = run_git_command(['git', 'checkout', '-b', branch_name, f'origin/{branch_name}'])
        if success:
            print(f"✓ Created local branch '{branch_name}' tracking 'origin/{branch_name}'")
            return True
        else:
            print(f"✗ Failed to create branch '{branch_name}': {output}")
    else:
        # Create new branch from current HEAD
        success, output = run_git_command(['git', 'checkout', '-b', branch_name])
        if success:
            print(f"✓ Created new branch '{branch_name}' from current HEAD")
            return True
        else:
            print(f"✗ Failed to create new branch '{branch_name}': {output}")
    
    return False


def switch_to_branch(target_branch: str = None) -> bool:
    """
    Switch to the specified branch or determine the best branch to switch to.
    Handles detached HEAD state gracefully.
    
    Args:
        target_branch: Specific branch name to switch to, or None for auto-detection
        
    Returns:
        True if successful, False otherwise
    """
    if target_branch is None:
        target_branch = get_default_branch()
        if target_branch is None:
            print("✗ No suitable branch found for checkout")
            return False
    
    print(f"Attempting to switch to branch: {target_branch}")
    
    # First, try direct checkout
    success, output = run_git_command(['git', 'checkout', target_branch])
    if success:
        print(f"✓ Successfully switched to branch '{target_branch}'")
        return True
    
    print(f"Direct checkout failed: {output}")
    
    # Check if branch exists in available branches
    available_branches = get_available_branches()
    print(f"Available branches: {', '.join(available_branches) if available_branches else 'None'}")
    
    if target_branch not in available_branches:
        print(f"Branch '{target_branch}' not found. Attempting to create it...")
        if create_branch_from_remote(target_branch):
            return True
        else:
            # Try alternative branch names
            alternatives = ['main', 'master'] if target_branch not in ['main', 'master'] else ['master', 'main']
            for alt_branch in alternatives:
                if alt_branch in available_branches:
                    print(f"Trying alternative branch: {alt_branch}")
                    success, _ = run_git_command(['git', 'checkout', alt_branch])
                    if success:
                        print(f"✓ Successfully switched to alternative branch '{alt_branch}'")
                        return True
                elif create_branch_from_remote(alt_branch):
                    return True
    
    print(f"✗ Failed to switch to any suitable branch")
    return False


def execute_git_push(target_branch: str = None, force: bool = False) -> bool:
    """
    Execute git push with robust branch handling.
    Handles detached HEAD state by switching to an appropriate branch first.
    
    Args:
        target_branch: Specific branch to switch to before pushing
        force: Whether to force push
        
    Returns:
        True if successful, False otherwise
    """
    print("=== Git Push Operation ===")
    
    # Check current git status
    success, status_output = run_git_command(['git', 'status', '--porcelain'])
    if not success:
        print(f"✗ Failed to get git status: {status_output}")
        return False
    
    # Check if we're in detached HEAD state
    if is_detached_head():
        print("⚠ Detected detached HEAD state")
        
        # Try to switch to a suitable branch
        if not switch_to_branch(target_branch):
            print("✗ Cannot proceed with push from detached HEAD state")
            return False
    else:
        # Get current branch
        success, current_branch = run_git_command(['git', 'branch', '--show-current'])
        if success and current_branch:
            print(f"Current branch: {current_branch}")
        else:
            print("⚠ Could not determine current branch")
            
            # Try to switch to target branch if specified
            if target_branch and not switch_to_branch(target_branch):
                return False
    
    # Get the current branch after potential switching
    success, current_branch = run_git_command(['git', 'branch', '--show-current'])
    if not success or not current_branch:
        print("✗ Could not determine current branch for push")
        return False
    
    print(f"Pushing branch: {current_branch}")
    
    # Prepare push command
    push_cmd = ['git', 'push']
    if force:
        push_cmd.append('--force')
    
    # Add origin and branch
    push_cmd.extend(['origin', current_branch])
    
    # Execute push
    success, output = run_git_command(push_cmd)
    if success:
        print(f"✓ Successfully pushed to origin/{current_branch}")
        return True
    else:
        print(f"✗ Push failed: {output}")
        
        # If push failed, try to set upstream
        if "no upstream branch" in output.lower() or "set-upstream" in output.lower():
            print("Attempting to set upstream branch...")
            upstream_cmd = ['git', 'push', '--set-upstream', 'origin', current_branch]
            success, upstream_output = run_git_command(upstream_cmd)
            if success:
                print(f"✓ Successfully set upstream and pushed to origin/{current_branch}")
                return True
            else:
                print(f"✗ Failed to set upstream: {upstream_output}")
        
        return False


def main():
    """
    Main function for command line usage.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Git utility for robust branch operations')
    parser.add_argument('--branch', '-b', help='Target branch name')
    parser.add_argument('--force', '-f', action='store_true', help='Force push')
    parser.add_argument('--push', action='store_true', help='Execute push operation')
    parser.add_argument('--switch', action='store_true', help='Only switch branch')
    
    args = parser.parse_args()
    
    if args.switch:
        success = switch_to_branch(args.branch)
    elif args.push:
        success = execute_git_push(args.branch, args.force)
    else:
        # Default: show available branches and current status
        print("=== Git Repository Status ===")
        if is_detached_head():
            print("⚠ Currently in detached HEAD state")
        
        available = get_available_branches()
        print(f"Available branches: {', '.join(available) if available else 'None'}")
        
        default = get_default_branch()
        if default:
            print(f"Recommended default branch: {default}")
        
        success = True
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()