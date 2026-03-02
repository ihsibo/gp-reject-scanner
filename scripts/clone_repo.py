#!/usr/bin/env python3
"""
Robust repository clone script for CI/CD workflows.
- Handles any repository with any branch name
- Automatically detects available branches
- Falls back gracefully to default branch
- Fresh clone without previous Git history
- Supports both public and private repositories
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"   Exit code: {e.returncode}")
        print(f"   Error: {e.stderr}")
        if check:
            sys.exit(1)
        return None, e.stderr


def get_available_branches(repo_url):
    """Get list of available branches from remote repository."""
    print("🔍 Checking available branches...")
    stdout, stderr = run_command(f"git ls-remote --heads {repo_url}", check=False)
    
    if not stdout:
        print(f"⚠️  Could not fetch branches: {stderr}")
        return []
    
    branches = []
    for line in stdout.split('\n'):
        if line.strip():
            # Extract branch name from refs/heads/branch-name
            if 'refs/heads/' in line:
                branch = line.split('refs/heads/')[1].strip()
                branches.append(branch)
    
    print(f"📋 Available branches: {', '.join(branches[:10])}{'...' if len(branches) > 10 else ''}")
    return branches


def clone_repository(repo_url, target_dir, preferred_branch=None, use_token=False, gh_token=None):
    """Clone repository with smart branch detection."""
    
    # Clean up target directory if it exists
    if Path(target_dir).exists():
        print(f"🧹 Cleaning up existing directory: {target_dir}")
        subprocess.run(f"rm -rf {target_dir}", shell=True)
    
    # Prepare repository URL with token if needed
    if use_token and gh_token:
        repo_url_with_token = f"https://{gh_token}@{repo_url.replace('https://', '')}"
    else:
        repo_url_with_token = repo_url
    
    # Get available branches
    available_branches = get_available_branches(repo_url)
    
    # Determine which branch to clone
    if preferred_branch and preferred_branch in available_branches:
        branch_to_clone = preferred_branch
        print(f"🎯 Using specified branch: {branch_to_clone}")
    else:
        if preferred_branch:
            print(f"⚠️  Preferred branch '{preferred_branch}' not found, using default branch")
        
        # Try to find default branch (often 'main' or 'master')
        default_branches = ['main', 'master', 'develop', 'dev']
        branch_to_clone = None
        
        for branch in default_branches:
            if branch in available_branches:
                branch_to_clone = branch
                print(f"🎯 Using default branch: {branch_to_clone}")
                break
        
        # Fallback to first available branch
        if not branch_to_clone and available_branches:
            branch_to_clone = available_branches[0]
            print(f"🎯 Using first available branch: {branch_to_clone}")
        else:
            print("❌ No branches found in repository")
            sys.exit(1)
    
    # Clone the repository
    print(f"🔍 Cloning repository: {repo_url}")
    print(f"📌 Branch: {branch_to_clone}")
    print(f"📁 Target directory: {target_dir}")
    
    if branch_to_clone:
        clone_cmd = f"git clone -b {branch_to_clone} --depth 1 {repo_url_with_token} {target_dir}"
    else:
        clone_cmd = f"git clone --depth 1 {repo_url_with_token} {target_dir}"
    
    stdout, stderr = run_command(clone_cmd, check=False)
    
    if stderr and "not found" in stderr.lower():
        print(f"❌ Clone failed: {stderr}")
        print("💡 This might be a private repository. Make sure you have proper access and token.")
        sys.exit(1)
    elif stderr:
        print(f"⚠️  Clone warning: {stderr}")
    
    # Verify successful clone
    if not Path(target_dir).exists():
        print("❌ Clone failed: Target directory was not created")
        sys.exit(1)
    
    # Verify we're on the correct branch
    stdout, stderr = run_command("git branch --show-current", cwd=target_dir, check=False)
    if stdout:
        actual_branch = stdout.strip()
        if actual_branch != branch_to_clone:
            print(f"⚠️  Warning: Expected branch {branch_to_clone}, but got {actual_branch}")
        else:
            print(f"✅ Successfully cloned branch: {actual_branch}")
    else:
        print("⚠️  Could not verify current branch")
    
    # Verify we have a clean Git repository
    stdout, _ = run_command("git status --porcelain", cwd=target_dir, check=False)
    if stdout:
        print("⚠️  Repository has uncommitted changes")
    else:
        print("✅ Repository is clean")
    
    print(f"🎉 Repository cloned successfully!")
    print(f"📂 Location: {Path(target_dir).absolute()}")
    
    # Show basic repository info
    stdout, _ = run_command("git log --oneline -1", cwd=target_dir, check=False)
    if stdout:
        print(f"📝 Latest commit: {stdout}")
    
    return branch_to_clone


def main():
    parser = argparse.ArgumentParser(description="Robust repository clone for CI/CD")
    parser.add_argument("repo_url", help="Repository URL to clone")
    parser.add_argument("target_dir", help="Target directory for clone")
    parser.add_argument("--branch", "-b", help="Preferred branch (default: auto-detect)")
    parser.add_argument("--token", "-t", help="GitHub token for private repos")
    parser.add_argument("--use-token", action="store_true", help="Use token for authentication")
    
    args = parser.parse_args()
    
    # Get GitHub token from environment if not provided
    gh_token = args.token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    
    try:
        cloned_branch = clone_repository(
            repo_url=args.repo_url,
            target_dir=args.target_dir,
            preferred_branch=args.branch,
            use_token=args.use_token or bool(gh_token),
            gh_token=gh_token
        )
        
        # Output branch info for CI consumption
        print(f"::set-output name=branch::{cloned_branch}")
        print(f"::set-output name=success::true")
        
    except KeyboardInterrupt:
        print("\n⚠️  Clone interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()