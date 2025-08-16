#!/usr/bin/env python3
"""
Test script for git_utils.py functionality.
Tests various scenarios including detached HEAD state.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from git_utils import (
    execute_git_push, 
    switch_to_branch, 
    get_available_branches, 
    is_detached_head,
    get_default_branch,
    run_git_command
)


def test_current_repository():
    """Test the functions in the current repository."""
    print("=== Testing Current Repository ===")
    
    # Test branch detection
    print("\n1. Testing branch detection:")
    branches = get_available_branches()
    print(f"Available branches: {branches}")
    
    # Test detached HEAD detection
    print("\n2. Testing detached HEAD detection:")
    detached = is_detached_head()
    print(f"Is detached HEAD: {detached}")
    
    # Test default branch detection
    print("\n3. Testing default branch detection:")
    default = get_default_branch()
    print(f"Default branch: {default}")
    
    # Test current status
    print("\n4. Current git status:")
    success, status = run_git_command(['git', 'status', '--short'])
    print(f"Status: {status if success else 'Failed to get status'}")
    
    return True


def test_branch_switching():
    """Test branch switching functionality."""
    print("\n=== Testing Branch Switching ===")
    
    # Get current branch
    success, current_branch = run_git_command(['git', 'branch', '--show-current'])
    print(f"Current branch: {current_branch if success else 'Unknown'}")
    
    # Test switching to default branch
    default_branch = get_default_branch()
    if default_branch:
        print(f"\nAttempting to switch to default branch: {default_branch}")
        success = switch_to_branch(default_branch)
        print(f"Switch result: {'Success' if success else 'Failed'}")
    
    return True


def simulate_detached_head():
    """Simulate detached HEAD state for testing."""
    print("\n=== Simulating Detached HEAD State ===")
    
    # Get current commit hash
    success, commit_hash = run_git_command(['git', 'rev-parse', 'HEAD'])
    if not success:
        print("Failed to get current commit hash")
        return False
    
    # Checkout the commit directly (creates detached HEAD)
    print(f"Checking out commit {commit_hash[:8]}... to simulate detached HEAD")
    success, output = run_git_command(['git', 'checkout', commit_hash])
    if success:
        print("Successfully created detached HEAD state")
        
        # Test detached HEAD detection
        detached = is_detached_head()
        print(f"Detached HEAD detected: {detached}")
        
        # Test switching from detached HEAD
        print("\nTesting switch from detached HEAD:")
        switch_success = switch_to_branch()
        print(f"Switch from detached HEAD: {'Success' if switch_success else 'Failed'}")
        
        return switch_success
    else:
        print(f"Failed to create detached HEAD: {output}")
        return False


def test_error_scenarios():
    """Test error handling scenarios."""
    print("\n=== Testing Error Scenarios ===")
    
    # Test switching to non-existent branch
    print("\n1. Testing switch to non-existent branch:")
    success = switch_to_branch("non_existent_branch_12345")
    print(f"Switch to non-existent branch: {'Unexpectedly succeeded' if success else 'Failed as expected'}")
    
    return True


def main():
    """Run all tests."""
    print("Git Utils Test Suite")
    print("=" * 50)
    
    # Store original directory
    original_dir = os.getcwd()
    
    try:
        # Change to repository directory
        repo_dir = "/home/runner/work/Cresta-Open-Data/Cresta-Open-Data"
        os.chdir(repo_dir)
        
        # Run tests
        test_current_repository()
        test_branch_switching()
        test_error_scenarios()
        
        # Note: Detached HEAD simulation is commented out to avoid disrupting the repository
        # It can be uncommented for thorough testing if needed
        # simulate_detached_head()
        
        print("\n" + "=" * 50)
        print("Test suite completed successfully!")
        
    except Exception as e:
        print(f"Test suite failed with error: {e}")
        return False
    finally:
        # Restore original directory
        os.chdir(original_dir)
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)