"""Tests for the token counter package."""

import os
import tempfile
import pytest
from pathlib import Path
from codebase_token_counter.token_counter import (
    count_tokens,
    is_binary,
    format_number,
    FILE_EXTENSIONS,
    TokenCounterConfig,
    process_repository,
    detect_file_encoding,
    read_file_with_encoding
)

def test_token_counting():
    """Test token counting functionality."""
    # Test basic token counting
    assert count_tokens("Hello, world!") > 0
    
    # Test empty string
    assert count_tokens("") == 0
    
    # Test whitespace
    assert count_tokens("   ") > 0
    
    # Test code snippet
    code = """
    def hello_world():
        print("Hello, world!")
    """
    assert count_tokens(code) > 0

def test_binary_file_detection():
    """Test binary file detection."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        # Write some text
        f.write(b"Hello, world!")
        text_path = f.name
    
    with tempfile.NamedTemporaryFile(delete=False) as f:
        # Write some binary data
        f.write(bytes(range(256)))
        binary_path = f.name
    
    try:
        assert not is_binary(text_path)
        assert is_binary(binary_path)
    finally:
        # Clean up
        os.unlink(text_path)
        os.unlink(binary_path)

def test_number_formatting():
    """Test number formatting functionality."""
    assert format_number(1000) == "1,000"
    assert format_number(1000000) == "1.0M"
    assert format_number(1500000) == "1.5M"
    assert format_number(1000000000) == "1.0B"
    assert format_number(0) == "0"

def test_file_extensions():
    """Test file extension mappings."""
    # Test common extensions
    assert FILE_EXTENSIONS[".py"] == "Python"
    assert FILE_EXTENSIONS[".js"] == "JavaScript"
    assert FILE_EXTENSIONS[".md"] == "Markdown"
    
    # Test case sensitivity
    assert ".py" in FILE_EXTENSIONS
    assert ".PY" not in FILE_EXTENSIONS
    
    # Test extension completeness
    assert len(FILE_EXTENSIONS) > 10  # Should have many extensions
    assert all(ext.startswith(".") for ext in FILE_EXTENSIONS)  # All should start with dot

def test_token_counter_config():
    """Test TokenCounterConfig functionality."""
    config = TokenCounterConfig()
    
    # Test default values
    assert '.git' in config.exclude_dirs
    assert 'node_modules' in config.exclude_dirs
    assert config.max_individual_files == 50
    
    # Test adding exclusions
    config.add_exclude_dirs(['custom_dir'])
    assert 'custom_dir' in config.exclude_dirs
    
    config.add_exclude_files(['test.txt'])
    assert 'test.txt' in config.exclude_files
    
    config.add_exclude_extensions(['log', '.tmp'])
    assert '.log' in config.exclude_extensions
    assert '.tmp' in config.exclude_extensions

def test_encoding_detection():
    """Test file encoding detection."""
    config = TokenCounterConfig()
    
    # Create a test file with UTF-8 content
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
        f.write("Hello, world! 🌍")
        test_path = f.name
    
    try:
        # Test encoding detection
        encoding = detect_file_encoding(test_path, config)
        assert encoding in ['utf-8', 'UTF-8']
        
        # Test reading with encoding
        content = read_file_with_encoding(test_path, config)
        assert content is not None
        assert "Hello, world!" in content
    finally:
        os.unlink(test_path)

def test_process_repository_simple():
    """Test the process_repository function with a simple test case."""
    # Create a temporary directory with test files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_files = {
            'test.py': 'print("Hello, world!")',
            'readme.md': '# Test\nThis is a test file.',
            'subdir/utils.py': 'def add(a, b):\n    return a + b'
        }
        
        for file_path, content in test_files.items():
            full_path = Path(temp_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        # Create config
        config = TokenCounterConfig()
        
        # Process the repository
        total_tokens, extension_stats, file_counts, directory_stats, all_files, all_directories = process_repository(
            temp_dir, config, total_only=False, debug=False, show_files=False
        )
        
        # Verify results
        assert isinstance(total_tokens, int)
        assert total_tokens > 0
        assert '.py' in extension_stats
        assert '.md' in extension_stats
        assert file_counts['.py'] == 2  # test.py and utils.py
        assert file_counts['.md'] == 1  # readme.md
        assert 'root' in all_directories
        assert 'subdir' in all_directories
        assert len(all_files) == 3

def test_total_only_mode():
    """Test the total_only flag functionality."""
    # Create a temporary directory with a test file
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / 'test.py'
        test_file.write_text('print("Hello, world!")')
        
        config = TokenCounterConfig()
        
        # Test with total_only=True
        total_tokens, extension_stats, file_counts, directory_stats, all_files, all_directories = process_repository(
            temp_dir, config, total_only=True, debug=False, show_files=False
        )
        assert total_tokens > 0
        assert isinstance(extension_stats, dict)
        assert isinstance(file_counts, dict)
        
        # Test with total_only=False
        total_tokens2, extension_stats2, file_counts2, directory_stats2, all_files2, all_directories2 = process_repository(
            temp_dir, config, total_only=False, debug=False, show_files=False
        )
        assert total_tokens2 == total_tokens  # Should be the same regardless of total_only flag
