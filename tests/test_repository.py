"""Tests for repository processing functionality."""

import os
import tempfile
import shutil
from pathlib import Path
from git import Repo
from codebase_token_counter.token_counter import process_repository, TokenCounterConfig

def create_test_repo():
    """Create a test repository with sample files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        repo = Repo.init(temp_dir)
        
        # Create some sample files
        files = {
            "main.py": "print('Hello, world!')\n",
            "README.md": "# Test Repository\n\nThis is a test.\n",
            "src/utils.py": "def add(a, b):\n    return a + b\n",
            "tests/test_utils.py": "def test_add():\n    assert add(1, 2) == 3\n",
            "static/style.css": "body { color: black; }\n",
        }
        
        # Create files and commit them
        for file_path, content in files.items():
            full_path = Path(temp_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            repo.index.add([str(full_path.relative_to(temp_dir))])
        
        # Commit the files
        repo.index.commit("Initial commit")
        
        yield temp_dir

def test_process_repository():
    """Test repository processing functionality."""
    for repo_path in create_test_repo():
        # Create config
        config = TokenCounterConfig()
        
        # Process the repository
        total_tokens, extension_stats, file_counts, directory_stats, all_files, all_directories = process_repository(
            repo_path, config, total_only=False, debug=False, show_files=False
        )
        
        # Verify results
        assert isinstance(total_tokens, int)
        assert isinstance(extension_stats, dict)
        assert isinstance(file_counts, dict)
        assert isinstance(directory_stats, dict)
        assert isinstance(all_files, list)
        assert isinstance(all_directories, set)
        assert total_tokens > 0
        
        # Check if we found all file types
        assert '.py' in extension_stats
        assert '.md' in extension_stats
        assert '.css' in extension_stats
        
        # Check file counts
        assert file_counts['.py'] == 3  # main.py, utils.py, test_utils.py
        assert file_counts['.md'] == 1  # README.md
        assert file_counts['.css'] == 1  # style.css
        
        # Check if token counts are reasonable
        for ext, count in extension_stats.items():
            assert count > 0  # Each file should have at least one token
        
        # Check directory stats
        assert 'root' in all_directories
        assert 'src' in all_directories
        assert 'tests' in all_directories
        assert 'static' in all_directories
        
        # Check all_files structure
        assert len(all_files) == 5  # Should have 5 files total
        for file_path, extension in all_files:
            assert os.path.exists(file_path)
            assert extension in ['.py', '.md', '.css']

def test_process_repository_with_exclusions():
    """Test repository processing with exclusions."""
    for repo_path in create_test_repo():
        # Create config with exclusions
        config = TokenCounterConfig()
        config.add_exclude_dirs(['tests'])
        config.add_exclude_extensions(['.css'])
        
        # Process the repository
        total_tokens, extension_stats, file_counts, directory_stats, all_files, all_directories = process_repository(
            repo_path, config, total_only=False, debug=False, show_files=False
        )
        
        # Verify exclusions worked
        assert '.css' not in extension_stats  # CSS files should be excluded
        assert file_counts.get('.css', 0) == 0  # No CSS files counted
        
        # Should still have Python and Markdown files
        assert '.py' in extension_stats
        assert '.md' in extension_stats
        
        # Should have fewer files due to exclusions
        assert len(all_files) < 5
