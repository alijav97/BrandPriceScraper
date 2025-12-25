#!/usr/bin/env python
"""
Push project to GitHub using GitPython
"""

import os
import sys

# Add the system Python path to use GitPython
sys.path.insert(0, r"c:\users\alija\appdata\local\programs\python\python314\lib\site-packages")

try:
    from git import Repo
    from git.exc import InvalidGitRepositoryError
except ImportError:
    print("Installing GitPython...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "gitpython"], check=True)
    from git import Repo
    from git.exc import InvalidGitRepositoryError

# Change to project directory
project_dir = r"c:\Users\alija\Downloads\London International - AI\Module C\App for self"
os.chdir(project_dir)

print("=" * 60)
print("📤 Pushing to GitHub")
print("=" * 60)

try:
    # Initialize repository if not already initialized
    try:
        repo = Repo(project_dir)
        print("✓ Repository already initialized")
    except InvalidGitRepositoryError:
        print("🔄 Initializing new repository...")
        repo = Repo.init(project_dir)
        print("✓ Repository initialized")
    
    # Configure git (required for commits)
    with repo.config_writer() as git_config:
        git_config.set_value("user", "name", "Brand Price Tracker").release()
        git_config.set_value("user", "email", "bot@brandpricetracker.local").release()
    
    print("✓ Git configured")
    
    # Add all files
    print("📁 Adding files...")
    try:
        repo.index.add([item for item in repo.untracked_files])
    except:
        pass
    repo.index.add(["*"])
    print(f"✓ Files staged ({len(repo.untracked_files)} untracked + tracked files)")
    
    # Commit
    print("📝 Creating commit...")
    try:
        commit = repo.index.commit("Initial commit: Brand Price Tracker application\n\nFeatures:\n- Multi-platform price scraping\n- Real-time data processing\n- Interactive Streamlit UI\n- CSV export capability")
        print(f"✓ Committed with hash: {commit.hexsha[:8]}")
    except Exception as e:
        print(f"Note: Commit info: {str(e)}")
    
    # Set up remote
    github_url = "https://github.com/alijav97/BrandPriceScraper.git"
    print(f"\n🔗 Configuring GitHub remote")
    print(f"   URL: {github_url}")
    
    try:
        repo.delete_remote("origin")
    except:
        pass
    
    origin = repo.create_remote("origin", github_url)
    print("✓ Remote configured")
    
    # Display status
    print("\n" + "=" * 60)
    print("📊 Git Repository Status")
    print("=" * 60)
    print(f"✓ Project: {os.path.basename(project_dir)}")
    print(f"✓ Path: {project_dir}")
    print(f"✓ Remote: {github_url}")
    print(f"✓ Branch: {repo.active_branch.name}")
    print(f"✓ Commits: {len(list(repo.iter_commits()))}")
    print(f"✓ Untracked files: {len(repo.untracked_files)}")
    
    # Show push command
    print("\n" + "=" * 60)
    print("🚀 To push to GitHub, run:")
    print("=" * 60)
    print(f"\ngit push -u origin {repo.active_branch.name}\n")
    
    print("=" * 60)
    print("✅ Repository ready for push!")
    print("=" * 60)
    print("\nNEXT STEPS:")
    print("1. Make sure your GitHub repo exists at:")
    print(f"   https://github.com/alijav97/BrandPriceScraper")
    print("2. If using HTTPS, you'll need a Personal Access Token")
    print("3. Run: git push -u origin main")
    print("\nOr if you have SSH set up:")
    print(f"   git remote set-url origin git@github.com:alijav97/BrandPriceScraper.git")
    print("   git push -u origin main")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
