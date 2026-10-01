#!/usr/bin/env python3

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "gitpython",
#   "tqdm",
#   "transformers",
#   "rich",
#   "chardet",
# ]
# ///

import os
import sys
import shutil
import tempfile
import warnings
import argparse
import chardet
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional

# Set environment variable to suppress transformers warnings
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

from git import Repo
from tqdm import tqdm
from transformers import AutoTokenizer
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich import print as rprint

try:
    from codebase_token_counter.model_registry import (
        PROVIDERS,
        ModelRecord,
        load_model_registry,
    )
except ModuleNotFoundError:  # Support running token_counter.py directly.
    from model_registry import PROVIDERS, ModelRecord, load_model_registry

# Initialize the console and tokenizer
warnings.filterwarnings('ignore')
console = Console()
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# File extensions mapped to their technologies
FILE_EXTENSIONS = {
    # Python and related
    '.py': 'Python',
    '.pyi': 'Python Interface',
    '.pyx': 'Cython',
    '.pxd': 'Cython Header',
    '.ipynb': 'Jupyter Notebook',
    '.requirements.txt': 'Python Requirements',
    '.pipfile': 'Python Pipenv',
    '.pyproject.toml': 'Python Project',
    '.txt': 'Plain Text',
    '.md': 'Markdown',
    '.pot': 'Translation Template',
    '.sample': 'Sample Configuration',

    # Web Technologies
    '.html': 'HTML',
    '.htm': 'HTML',
    '.css': 'CSS',
    '.scss': 'SASS',
    '.sass': 'SASS',
    '.less': 'LESS',
    '.js': 'JavaScript',
    '.jsx': 'React JSX',
    '.ts': 'TypeScript',
    '.tsx': 'React TSX',
    '.vue': 'Vue.js',
    '.svelte': 'Svelte',
    '.php': 'PHP',
    '.blade.php': 'Laravel Blade',
    '.hbs': 'Handlebars',
    '.ejs': 'EJS Template',
    '.astro': 'Astro',

    # System Programming
    '.c': 'C',
    '.h': 'C Header',
    '.cpp': 'C++',
    '.hpp': 'C++ Header',
    '.cc': 'C++',
    '.hh': 'C++ Header',
    '.cxx': 'C++',
    '.rs': 'Rust',
    '.go': 'Go',
    '.swift': 'Swift',
    '.m': 'Objective-C',
    '.mm': 'Objective-C++',

    # JVM Languages
    '.java': 'Java',
    '.class': 'Java Bytecode',
    '.jar': 'Java Archive',
    '.kt': 'Kotlin',
    '.kts': 'Kotlin Script',
    '.groovy': 'Groovy',
    '.scala': 'Scala',
    '.clj': 'Clojure',

    # .NET Languages
    '.cs': 'C#',
    '.vb': 'Visual Basic',
    '.fs': 'F#',
    '.fsx': 'F# Script',
    '.xaml': 'XAML',

    # Shell and Scripts
    '.sh': 'Shell Script',
    '.bash': 'Bash Script',
    '.zsh': 'Zsh Script',
    '.fish': 'Fish Script',
    '.ps1': 'PowerShell',
    '.bat': 'Batch File',
    '.cmd': 'Windows Command',
    '.nu': 'Nushell Script',

    # Ruby and Related
    '.rb': 'Ruby',
    '.erb': 'Ruby ERB Template',
    '.rake': 'Ruby Rake',
    '.gemspec': 'Ruby Gem Spec',

    # Other Programming Languages
    '.pl': 'Perl',
    '.pm': 'Perl Module',
    '.ex': 'Elixir',
    '.exs': 'Elixir Script',
    '.erl': 'Erlang',
    '.hrl': 'Erlang Header',
    '.hs': 'Haskell',
    '.lhs': 'Literate Haskell',
    '.hcl': 'HCL (Terraform)',
    '.lua': 'Lua',
    '.r': 'R',
    '.rmd': 'R Markdown',
    '.jl': 'Julia',
    '.dart': 'Dart',
    '.nim': 'Nim',
    '.ml': 'OCaml',
    '.mli': 'OCaml Interface',

    # Configuration and Data
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.toml': 'TOML',
    '.ini': 'INI',
    '.conf': 'Configuration',
    '.config': 'Configuration',
    '.env': 'Environment Variables',
    '.properties': 'Properties',
    '.xml': 'XML',
    '.xsd': 'XML Schema',
    '.dtd': 'Document Type Definition',
    '.csv': 'CSV',
    '.tsv': 'TSV',

    # Documentation and Text
    '.md': 'Markdown',
    '.mdx': 'MDX',
    '.rst': 'reStructuredText',
    '.txt': 'Plain Text',
    '.tex': 'LaTeX',
    '.adoc': 'AsciiDoc',
    '.wiki': 'Wiki Markup',
    '.org': 'Org Mode',

    # Database
    '.sql': 'SQL',
    '.psql': 'PostgreSQL',
    '.plsql': 'PL/SQL',
    '.tsql': 'T-SQL',
    '.prisma': 'Prisma Schema',

    # Build and Package
    '.gradle': 'Gradle',
    '.maven': 'Maven POM',
    '.cmake': 'CMake',
    '.make': 'Makefile',
    '.dockerfile': 'Dockerfile',
    '.containerfile': 'Container File',
    '.nix': 'Nix Expression',

    # Web Assembly
    '.wat': 'WebAssembly Text',
    '.wasm': 'WebAssembly Binary',

    # GraphQL
    '.graphql': 'GraphQL',
    '.gql': 'GraphQL',

    # Protocol Buffers and gRPC
    '.proto': 'Protocol Buffers',

    # Mobile Development
    '.xcodeproj': 'Xcode Project',
    '.pbxproj': 'Xcode Project',
    '.gradle': 'Android Gradle',
    '.plist': 'Property List',

    # Game Development
    '.unity': 'Unity Scene',
    '.prefab': 'Unity Prefab',
    '.godot': 'Godot Resource',
    '.tscn': 'Godot Scene',

    # AI/ML
    '.onnx': 'ONNX Model',
    '.h5': 'HDF5 Model',
    '.pkl': 'Pickle Model',
    '.model': 'Model File',
}

# Set of all text extensions for quick lookup
TEXT_EXTENSIONS = set(FILE_EXTENSIONS.keys())

class TokenCounterConfig:
    """Configuration class for token counter settings"""
    def __init__(self):
        self.exclude_dirs: Set[str] = {'.git', 'venv', '.venv', '__pycache__', '.pytest_cache', '.mypy_cache', 'node_modules', '.next', 'build', 'dist', '.github', '.roo', '.vscode', '.cursor'}
        self.exclude_files: Set[str] = {"token_counter.py", "llm_pricing_data.json", ".gitignore", ".luarc.json", ".markdownlint.json", ".rooignore", ".roomodes", "assistant.pot"}
        self.exclude_extensions: Set[str] = set()
        self.max_individual_files: int = 50
        self.force_encoding: Optional[str] = None
        self.fallback_encodings: List[str] = ['utf-8', 'latin1', 'cp1252', 'ascii']
        
    def add_exclude_dirs(self, dirs: List[str]):
        """Add directories to exclude"""
        self.exclude_dirs.update(dirs)
        
    def add_exclude_files(self, files: List[str]):
        """Add files to exclude"""
        self.exclude_files.update(files)
        
    def add_exclude_extensions(self, extensions: List[str]):
        """Add extensions to exclude"""
        # Normalize extensions (add . if missing)
        normalized = {ext if ext.startswith('.') else f'.{ext}' for ext in extensions}
        self.exclude_extensions.update(normalized)

def detect_file_encoding(file_path: str, config: TokenCounterConfig) -> str:
    """Detect file encoding using chardet or fall back to specified encodings"""
    if config.force_encoding:
        return config.force_encoding
    
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB for detection
            result = chardet.detect(raw_data)
            if result['encoding'] and result['confidence'] > 0.7:
                return result['encoding']
    except Exception:
        pass
    
    # Fall back to trying encodings in order
    for encoding in config.fallback_encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read(1000)  # Try to read some content
                return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    return 'utf-8'  # Last resort

def read_file_with_encoding(file_path: str, config: TokenCounterConfig) -> Optional[str]:
    """Read file content with proper encoding handling"""
    encoding = detect_file_encoding(file_path, config)
    
    for attempt_encoding in [encoding] + config.fallback_encodings:
        try:
            with open(file_path, 'r', encoding=attempt_encoding, errors='replace') as f:
                return f.read()
        except Exception as e:
            continue
    
    # If all encodings fail, return None
    return None

def should_exclude_file(file_path: str, repo_path: str, config: TokenCounterConfig) -> bool:
    """Check if a file should be excluded from token counting."""
    relative_path = os.path.relpath(file_path, repo_path)
    filename = os.path.basename(file_path)
    
    # Check excluded files
    if filename in config.exclude_files or relative_path in config.exclude_files:
        return True
    
    # Check file patterns
    for pattern in config.exclude_files:
        if pattern in relative_path or pattern in filename:
            return True
    
    # Check extensions
    if '.' in filename:
        # Handle special cases first
        if filename.endswith('.lua.sample'):
            extension = '.lua'
        elif filename.endswith('.pot'):
            extension = '.pot'
        else:
            extension = '.' + filename.split('.')[-1].lower()
            
        if extension in config.exclude_extensions:
            return True
    
    return False

def should_exclude_directory(dir_path: str, repo_path: str, config: TokenCounterConfig) -> bool:
    """Check if a directory should be excluded"""
    relative_path = os.path.relpath(dir_path, repo_path)
    dir_name = os.path.basename(dir_path)
    
    # Check if directory name is in exclude list
    if dir_name in config.exclude_dirs:
        return True
    
    # Check if any part of the path matches exclude patterns
    path_parts = relative_path.split(os.sep)
    for part in path_parts:
        if part in config.exclude_dirs:
            return True
    
    return False

def extract_corrected_stats_from_tree(tree: Dict) -> Dict[str, Dict]:
    """Extract corrected directory stats from tree structure after calculate_totals"""
    corrected_stats = {}
    
    def traverse_tree(node_dict: Dict, path_prefix: str = ""):
        for name, data in node_dict.items():
            # Determine the full path for this directory
            if name == 'root':
                full_path = 'root'
            else:
                full_path = f"{path_prefix}/{name}" if path_prefix and path_prefix != 'root' else name
                
            # Store the corrected data
            corrected_stats[full_path] = {
                'tokens': data.get('tokens', 0),
                'files': data.get('files', 0),
                'path': data.get('path', full_path)
            }
            
            # Recursively process children
            if data.get('children'):
                traverse_tree(data['children'], full_path if full_path != 'root' else "")
    
    traverse_tree(tree)
    return corrected_stats

def create_flat_directory_structure(directory_stats: Dict[str, int], file_counts_by_dir: Dict[str, int], all_directories: Set[str], corrected_stats: Dict[str, Dict] = None) -> Dict[str, Dict]:
    """Create a flat directory structure without nesting"""
    flat_structure = {}
    
    # Include all directories, even empty ones
    for directory in sorted(all_directories):
        display_name = f"📁 {directory}" if directory != 'root' else "📁 root"
        
        # Use corrected stats if available, otherwise fall back to original stats
        if corrected_stats and directory in corrected_stats:
            tokens = corrected_stats[directory]['tokens']
            files = corrected_stats[directory]['files']
        else:
            tokens = directory_stats.get(directory, 0)
            files = file_counts_by_dir.get(directory, 0)
        
        flat_structure[display_name] = {
            'tokens': tokens,
            'files': files,
            'path': directory
        }
    
    return flat_structure

def create_tree_directory_structure(directory_stats: Dict[str, int], file_counts_by_dir: Dict[str, int], all_directories: Set[str], show_empty: bool = True, sort_by_tokens: bool = False, root_name: str = "root") -> List[Tuple[str, Dict]]:
    """Create a hierarchical tree directory structure"""
    
    # Build directory tree with proper root structure
    tree = {}
    
    # Sort directories to ensure parents come before children
    sorted_dirs = sorted(all_directories, key=lambda x: (x.count('/'), x))
    
    for directory in sorted_dirs:
        tokens = directory_stats.get(directory, 0)
        files = file_counts_by_dir.get(directory, 0)
        
        # Skip empty directories if not showing them
        if not show_empty and tokens == 0 and files == 0:
            continue
            
        # Build proper tree structure
        if directory == 'root':
            parts = ['root']
        else:
            # All other directories are children of root
            parts = ['root'] + directory.split('/')
        
        current = tree
        
        # Build path in tree - create all nodes including the final one
        for i, part in enumerate(parts):
            if part not in current:
                # Calculate the actual directory path for this node
                if i == 0:  # root node
                    node_path = 'root'
                else:
                    # For all other nodes, construct path properly
                    node_path = '/'.join(parts[1:i+1]) if i > 0 else 'root'
                
                current[part] = {
                    'children': {},
                    'tokens': 0,
                    'files': 0,
                    'path': node_path,
                    'is_leaf': False
                }
            
            # Only set actual data for the final directory in the path
            if i == len(parts) - 1:
                current[part]['tokens'] += tokens  # ADD to existing tokens, don't overwrite
                current[part]['files'] += files    # ADD to existing files, don't overwrite
                current[part]['is_leaf'] = True
                current[part]['path'] = directory
            
            # Move to children for next iteration (except for the last part)
            if i < len(parts) - 1:
                current = current[part]['children']
    
    # Calculate totals for parent directories
    def calculate_totals(node_dict: Dict):
        """Recursively calculate totals for parent directories"""
        for name, data in node_dict.items():
            if data.get('children'):
                # First calculate totals for children
                calculate_totals(data['children'])
                # Then sum up children's tokens and files
                child_tokens = sum(child.get('tokens', 0) for child in data['children'].values())
                child_files = sum(child.get('files', 0) for child in data['children'].values())
                # Add to existing tokens/files (for directories that have both files and subdirs)
                data['tokens'] = data.get('tokens', 0) + child_tokens
                data['files'] = data.get('files', 0) + child_files
    
    calculate_totals(tree)
    
    def tree_to_list(node_dict: Dict, indent_level: int = 0, sort_by_tokens: bool = False) -> List[Tuple[str, Dict]]:
        """Convert tree structure to flat list with proper sorting"""
        result = []
        
        if sort_by_tokens:
            # When sorting by tokens, ignore hierarchy and sort everything by token count
            sorted_items = sorted(node_dict.items(), key=lambda x: (
                x[1].get('tokens', 0) == 0,  # Empty items last
                -x[1].get('tokens', 0),      # Highest tokens first
                x[0]                         # Alphabetical fallback
            ))
            
            for name, data in sorted_items:
                tokens = data.get('tokens', 0)
                files = data.get('files', 0)
                path = data.get('path', name)
                
                # Skip if no tokens and not showing empty
                if not show_empty and tokens == 0 and files == 0:
                    continue
                
                # Create display name with simple indentation
                indent = "  " * indent_level
                display_name = f"{indent}📁 {name}"
                
                result.append((display_name, {
                    'tokens': tokens,
                    'files': files,
                    'path': path,
                    'is_empty': tokens == 0 and files == 0
                }))
                
                # Recursively add children
                if data.get('children'):
                    result.extend(tree_to_list(data['children'], indent_level + 1, sort_by_tokens))
        else:
            # Default: subdirectories first, then files at bottom
            # Special handling for root level (indent_level == 0)
            if indent_level == 0 and 'root' in node_dict:
                # Handle root specially
                root_data = node_dict['root']
                tokens = root_data.get('tokens', 0)
                files = root_data.get('files', 0)
                path = root_data.get('path', 'root')
                
                # Add root directory header
                result.append((f"📁 {root_name}", {
                    'tokens': tokens,
                    'files': files,
                    'path': path,
                    'is_empty': tokens == 0 and files == 0
                }))
                
                # Process root's children: subdirectories first, then files
                if root_data.get('children'):
                    children = root_data['children']
                    
                    # Separate subdirectories from files
                    subdirectories = []
                    root_files = []
                    
                    for child_name, child_data in children.items():
                        if child_data.get('children'):
                            # This is a subdirectory
                            subdirectories.append((child_name, child_data))
                        else:
                            # This is a file at root level
                            root_files.append((child_name, child_data))
                    
                    # Sort subdirectories by token count (descending)
                    subdirectories.sort(key=lambda x: (
                        x[1].get('tokens', 0) == 0,  # Empty last
                        -x[1].get('tokens', 0),      # Highest tokens first
                        x[0]                         # Alphabetical fallback
                    ))
                    
                    # Add subdirectories first
                    for name, data in subdirectories:
                        tokens = data.get('tokens', 0)
                        files = data.get('files', 0)
                        path = data.get('path', name)
                        
                        if not show_empty and tokens == 0 and files == 0:
                            continue
                        
                        display_name = f"  📁 {name}"
                        result.append((display_name, {
                            'tokens': tokens,
                            'files': files,
                            'path': path,
                            'is_empty': tokens == 0 and files == 0
                        }))
                        
                        # Recursively add children
                        if data.get('children'):
                            result.extend(tree_to_list(data['children'], 2, sort_by_tokens))
                    
                    # Sort root files by token count (descending)
                    root_files.sort(key=lambda x: (
                        x[1].get('tokens', 0) == 0,  # Empty last
                        -x[1].get('tokens', 0),      # Highest tokens first
                        x[0]                         # Alphabetical fallback
                    ))
                    
                    # Add root files at the bottom
                    for name, data in root_files:
                        tokens = data.get('tokens', 0)
                        files = data.get('files', 0)
                        path = data.get('path', name)
                        
                        if not show_empty and tokens == 0 and files == 0:
                            continue
                        
                        display_name = f"  📁 {name}"
                        result.append((display_name, {
                            'tokens': tokens,
                            'files': files,
                            'path': path,
                            'is_empty': tokens == 0 and files == 0
                        }))
            else:
                # For non-root levels, use original logic
                # Separate directories with children from leaf directories
                dirs_with_children = []
                leaf_dirs = []
                
                for name, data in node_dict.items():
                    if data.get('children'):
                        dirs_with_children.append((name, data))
                    else:
                        leaf_dirs.append((name, data))
                
                # Sort directories with children by token count (descending)
                dirs_with_children.sort(key=lambda x: (
                    x[1].get('tokens', 0) == 0,  # Empty last
                    -x[1].get('tokens', 0),      # Highest tokens first
                    x[0]                         # Alphabetical fallback
                ))
                
                # Sort leaf directories by token count
                leaf_dirs.sort(key=lambda x: (
                    x[1].get('tokens', 0) == 0,  # Empty last
                    -x[1].get('tokens', 0),      # Highest tokens first
                    x[0]                         # Alphabetical fallback
                ))
                
                # Combine: subdirectories first, then leaf items at bottom
                sorted_items = dirs_with_children + leaf_dirs
                
                for name, data in sorted_items:
                    tokens = data.get('tokens', 0)
                    files = data.get('files', 0)
                    path = data.get('path', name)
                    
                    # Skip if no tokens and not showing empty
                    if not show_empty and tokens == 0 and files == 0:
                        continue
                    
                    # Create display name with simple indentation
                    indent = "  " * indent_level
                    display_name = f"{indent}📁 {name}"
                    
                    result.append((display_name, {
                        'tokens': tokens,
                        'files': files,
                        'path': path,
                        'is_empty': tokens == 0 and files == 0
                    }))
                    
                    # Recursively add children
                    if data.get('children'):
                        result.extend(tree_to_list(data['children'], indent_level + 1, sort_by_tokens))
        
        return result
    
    # Start from root level
    result = []
    
    if 'root' in tree:
        # Show the complete tree starting from root
        result = tree_to_list(tree, 0, sort_by_tokens)
    else:
        result = tree_to_list(tree, 0, sort_by_tokens)
    
    return result

def process_repository(repo_path: str, config: TokenCounterConfig, total_only: bool = False, debug: bool = False, show_files: bool = False) -> Tuple[int, Dict[str, int], Dict[str, int], Dict[str, int], List[Tuple[str, str]], Set[str]]:
    """Process all files in the repository and count tokens."""
    total_tokens = 0
    extension_stats = {}
    file_counts = {}
    directory_stats = {}
    all_directories = set()

    # Normalize the repository path
    repo_path = os.path.abspath(repo_path)
    
    if debug:
        console.print(f"[bold cyan]Starting repository scan at: {repo_path}[/bold cyan]")
        console.print(f"[cyan]Excluded directories: {sorted(config.exclude_dirs)}[/cyan]")
        console.print(f"[cyan]Excluded files: {sorted(config.exclude_files)}[/cyan]")
        console.print(f"[cyan]Excluded extensions: {sorted(config.exclude_extensions)}[/cyan]")

    # Get list of all files and track all directories
    all_files = []
    total_dirs_processed = 0
    
    try:
        for root, dirs, files in os.walk(repo_path):
            total_dirs_processed += 1
            
            # Track this directory
            rel_root = os.path.relpath(root, repo_path) if root != repo_path else "root"
            all_directories.add(rel_root)
            
            # Filter out excluded directories
            original_dirs = dirs.copy()
            dirs[:] = [d for d in dirs if not should_exclude_directory(os.path.join(root, d), repo_path, config)]
            
            if debug:
                excluded = [d for d in original_dirs if d not in dirs]
                if excluded:
                    console.print(f"[red]Excluding directories in {rel_root}: {excluded}[/red]")
                console.print(f"[blue]Processing directory: {rel_root} ({len(files)} files, {len(dirs)} subdirs)[/blue]")
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip excluded files
                if should_exclude_file(file_path, repo_path, config):
                    if debug:
                        console.print(f"[red]Excluding file: {os.path.relpath(file_path, repo_path)}[/red]")
                    continue
                
                # Get extension - handle multiple dots properly
                if '.' in file:
                    # Handle special cases first
                    if file.endswith('.lua.sample'):
                        extension = '.lua'
                    elif file.endswith('.pot'):
                        extension = '.pot'
                    else:
                        extension = '.' + file.split('.')[-1].lower()
                else:
                    if debug and not file.startswith('.'):
                        console.print(f"[yellow]Skipping file without extension: {os.path.relpath(file_path, repo_path)}[/yellow]")
                    continue
                    
                if extension in FILE_EXTENSIONS:
                    try:
                        # Check if file is binary before adding to list
                        if not is_binary(file_path):
                            all_files.append((file_path, extension))
                            file_counts[extension] = file_counts.get(extension, 0) + 1
                            if debug:
                                console.print(f"[green]✓ Added: {os.path.relpath(file_path, repo_path)} ({extension})[/green]")
                        else:
                            if debug:
                                console.print(f"[yellow]Skipping binary file: {os.path.relpath(file_path, repo_path)}[/yellow]")
                    except (OSError, IOError, UnicodeDecodeError) as e:
                        if debug:
                            console.print(f"[red]Error accessing file {os.path.relpath(file_path, repo_path)}: {e}[/red]")
                        continue
                else:
                    if debug and extension not in {'.gitignore', '.DS_Store', '.pyc'} and not file.startswith('.'):
                        console.print(f"[yellow]Unsupported extension: {os.path.relpath(file_path, repo_path)} ({extension})[/yellow]")
                        
    except Exception as e:
        if debug:
            console.print(f"[red]Error during directory traversal: {e}[/red]")
        raise

    if debug:
        console.print(f"\n[bold cyan]Scan complete![/bold cyan]")
        console.print(f"[cyan]Total directories found: {len(all_directories)}[/cyan]")
        console.print(f"[cyan]Total files found: {len(all_files)}[/cyan]")
    
    # Process files with improved encoding handling
    encoding_issues = []
    for file_path, extension in (track(all_files, description="[bold blue]Processing files") if not total_only else all_files):
        try:
            content = read_file_with_encoding(file_path, config)
            if content is None:
                encoding_issues.append(os.path.relpath(file_path, repo_path))
                if not total_only:
                    console.print(f"[red]Could not read file with any encoding: {os.path.relpath(file_path, repo_path)}[/red]")
                continue
                
            tokens = count_tokens(content)
            total_tokens += tokens
            
            if extension not in extension_stats:
                extension_stats[extension] = tokens
            else:
                extension_stats[extension] += tokens
            
            # Track tokens by directory
            relative_path = os.path.relpath(file_path, repo_path)
            dir_path = os.path.dirname(relative_path)
            directory = 'root' if dir_path in ('', '.') else dir_path
            
            # Ensure directory is tracked
            all_directories.add(directory)
            
            # Update directory stats
            if directory not in directory_stats:
                directory_stats[directory] = tokens
            else:
                directory_stats[directory] += tokens
                    
        except Exception as e:
            if not total_only:
                console.print(f"[red]Error processing {file_path}: {str(e)}[/red]")
    
    # Report encoding issues summary
    if encoding_issues and not total_only:
        console.print(f"\n[yellow]⚠️  {len(encoding_issues)} files had encoding issues. Try --encoding option or check file formats.[/yellow]")

    return total_tokens, extension_stats, file_counts, directory_stats, all_files, all_directories

def _format_token_limit(token_limit: int) -> str:
    """Format a context-window limit for the comparison table."""
    if token_limit >= 1000000:
        return f"{token_limit / 1000000:.1f}M"
    if token_limit >= 1000:
        return f"{token_limit / 1000:.0f}K"
    return str(token_limit)


def create_context_window_table(
    total_tokens: int, models: List[ModelRecord]
) -> Tuple[Table, List[str]]:
    """Build the context comparison table using registry-owned model metadata."""
    context_table = Table(title="\n[bold]Context Window Comparisons[/bold]")
    context_table.add_column("Model", style="blue")
    context_table.add_column("Input Limit", justify="right", style="cyan")
    context_table.add_column("Input Usage", justify="right")
    context_table.add_column("Output Limit", justify="right", style="cyan")
    context_table.add_column("Status", justify="center")

    fits_entirely = []
    grouped_models = {provider: [] for provider in PROVIDERS}

    for model in models:
        input_percentage = (total_tokens / model.max_input_tokens) * 100
        if input_percentage <= 100:
            color = "green"
            status = "✅ Fits"
            fits_entirely.append(model.display_name)
        elif input_percentage <= 150:
            color = "yellow"
            status = "⚠️  Tight"
        else:
            color = "red"
            status = "❌ Too Big"

        grouped_models[model.provider].append(
            (
                model.display_name,
                _format_token_limit(model.max_input_tokens),
                input_percentage,
                color,
                _format_token_limit(model.max_output_tokens),
                status,
            )
        )

    for provider_name, provider_models in grouped_models.items():
        if not provider_models:
            continue

        context_table.add_row(f"[bold]{provider_name}[/bold]", "", "", "", "")
        provider_models.sort(key=lambda model: model[2])
        for model, input_limit, input_percentage, color, output_limit, status in provider_models:
            context_table.add_row(
                f"  {model}",
                input_limit,
                f"[{color}]{input_percentage:.1f}%[/{color}]",
                output_limit,
                status,
            )

    return context_table, fits_entirely


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Count tokens in a repository with advanced exclusion and encoding support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/repo --exclude-dirs node_modules,build --exclude-extensions .log,.tmp
  %(prog)s https://github.com/user/repo --encoding latin1 --max-files 100 --tree
  %(prog)s . --total --exclude-files "*.test.*,*.spec.*"
  %(prog)s /path/to/repo --flat --hide-empty --sort-by-tokens
        """
    )
    
    parser.add_argument('target', help='Repository URL or local directory path')
    parser.add_argument('--total', '-t', action='store_true', help='Only output the total token count')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug output')
    parser.add_argument('--files', '-f', action='store_true', help='Show individual files within directories')
    
    # Exclusion options
    parser.add_argument('--exclude-dirs', help='Comma-separated list of directories to exclude (e.g., node_modules,build,dist)')
    parser.add_argument('--exclude-files', help='Comma-separated list of file patterns to exclude (e.g., "*.test.*,*.log,temp*")')
    parser.add_argument('--exclude-extensions', help='Comma-separated list of extensions to exclude (e.g., .log,.tmp,.cache)')
    
    # Encoding options
    parser.add_argument('--encoding', help='Force specific encoding (e.g., utf-8, latin1, cp1252)')
    parser.add_argument('--fallback-encodings', help='Comma-separated list of fallback encodings to try')
    
    # Display options
    parser.add_argument('--max-files', type=int, default=50, help='Maximum number of individual files to show (default: 50)')
    parser.add_argument('--tree', action='store_true', default=True, help='Show directory structure as tree (default)')
    parser.add_argument('--flat', action='store_true', help='Show directory structure as flat list')
    parser.add_argument('--show-empty', action='store_true', default=True, help='Show empty directories (default)')
    parser.add_argument('--hide-empty', action='store_true', help='Hide empty directories')
    parser.add_argument('--sort-by-tokens', action='store_true', help='Sort directories by token count instead of hierarchy')
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Create configuration
    config = TokenCounterConfig()
    
    # Apply command line overrides
    if args.exclude_dirs:
        config.add_exclude_dirs([d.strip() for d in args.exclude_dirs.split(',')])
    
    if args.exclude_files:
        config.add_exclude_files([f.strip() for f in args.exclude_files.split(',')])
    
    if args.exclude_extensions:
        config.add_exclude_extensions([e.strip() for e in args.exclude_extensions.split(',')])
    
    if args.encoding:
        config.force_encoding = args.encoding
    
    if args.fallback_encodings:
        config.fallback_encodings = [e.strip() for e in args.fallback_encodings.split(',')]
    
    config.max_individual_files = args.max_files
    
    # Handle display options
    use_tree = args.tree and not args.flat
    show_empty = args.show_empty and not args.hide_empty
    sort_by_tokens = args.sort_by_tokens
    
    # Suppress all warnings if total_only is True
    if args.total:
        import logging
        logging.getLogger('transformers').setLevel(logging.ERROR)

    temp_dir = None
    target = args.target

    # Check if the target is a local directory
    if os.path.isdir(target):
        if not args.total:
            console.print(f"[green]Analyzing local directory: {target}[/green]")
        analyze_path = target
    else:
        # Clone the repository to a temporary directory
        temp_dir = tempfile.mkdtemp()
        if not args.total:
            console.print(f"[yellow]Cloning repository: {target}[/yellow]")
        try:
            Repo.clone_from(target, temp_dir)
            analyze_path = temp_dir
        except Exception as e:
            console.print(f"[red]Error cloning repository: {str(e)}[/red]")
            shutil.rmtree(temp_dir)
            sys.exit(1)

    try:
        total_tokens, extension_stats, file_counts, directory_stats, all_files, all_directories = process_repository(analyze_path, config, args.total, args.debug, args.files)
        
        model_registry = load_model_registry()
        
    except Exception as e:
        if not args.total:
            console.print(f"[red]Error analyzing repository: {str(e)}[/red]")
        if temp_dir:
            shutil.rmtree(temp_dir)
        sys.exit(1)

    # Print results
    if args.total:
        # Only print the total number
        print(total_tokens)
    else:
        console.print("\n[bold cyan]Results:[/bold cyan]")
        console.print(f"Total tokens: [green]{format_number(total_tokens)}[/green] ({total_tokens:,})")

    if not args.total:
        # Create and populate extension table
        ext_table = Table(title="\n[bold]Tokens by file extension[/bold]")
        ext_table.add_column("Extension", style="cyan")
        ext_table.add_column("Tokens", justify="right", style="green")
        ext_table.add_column("Files", justify="right", style="yellow")

        for ext, count in sorted(extension_stats.items(), key=lambda x: x[1], reverse=True):
            ext_table.add_row(
                ext,
                f"{format_number(count)}",
                f"{file_counts[ext]} file{'s' if file_counts[ext] != 1 else ''}"
            )
        console.print(ext_table)

        # Group results by technology category
        tech_stats = {}
        tech_file_counts = {}
        for ext, count in extension_stats.items():
            tech = FILE_EXTENSIONS[ext]
            tech_stats[tech] = tech_stats.get(tech, 0) + count
            tech_file_counts[tech] = tech_file_counts.get(tech, 0) + file_counts[ext]

        # Create and populate technology table
        tech_table = Table(title="\n[bold]Tokens by Technology[/bold]")
        tech_table.add_column("Technology", style="magenta")
        tech_table.add_column("Tokens", justify="right", style="green")
        tech_table.add_column("Files", justify="right", style="yellow")

        for tech, count in sorted(tech_stats.items(), key=lambda x: x[1], reverse=True):
            tech_table.add_row(
                tech,
                f"{format_number(count)}",
                f"{tech_file_counts[tech]} file{'s' if tech_file_counts[tech] != 1 else ''}"
            )
        console.print(tech_table)

        # Create directory breakdown table
        structure_type = "Tree Structure" if use_tree else "Flat Structure"
        dir_table = Table(title=f"\n[bold]Tokens by Directory ({structure_type})[/bold]")
        dir_table.add_column("Directory", style="magenta")
        dir_table.add_column("Tokens", justify="right", style="green")
        dir_table.add_column("Percentage", justify="right", style="yellow")
        dir_table.add_column("Files", justify="right", style="cyan")

        # Count files by directory for the table
        file_counts_by_dir = {}
        for file_path, ext in all_files:
            relative_path = os.path.relpath(file_path, analyze_path)
            dir_path = os.path.dirname(relative_path)
            directory = 'root' if dir_path in ('', '.') else dir_path
            file_counts_by_dir[directory] = file_counts_by_dir.get(directory, 0) + 1

        # Create tree structure first to get corrected totals
        root_folder_name = os.path.basename(os.path.abspath(analyze_path))
        tree_structure = create_tree_directory_structure(directory_stats, file_counts_by_dir, all_directories, show_empty, sort_by_tokens, root_folder_name)
        
        # Extract corrected stats from tree structure for flat structure
        # First we need to rebuild the tree internally to get the corrected stats
        tree = {}
        sorted_dirs = sorted(all_directories, key=lambda x: (x.count('/'), x))
        
        for directory in sorted_dirs:
            tokens = directory_stats.get(directory, 0)
            files = file_counts_by_dir.get(directory, 0)
            
            if directory == 'root':
                parts = ['root']
            else:
                parts = ['root'] + directory.split('/')
            
            current = tree
            for i, part in enumerate(parts):
                if part not in current:
                    node_path = 'root' if i == 0 else '/'.join(parts[1:i+1]) if i > 0 else 'root'
                    current[part] = {
                        'children': {},
                        'tokens': 0,
                        'files': 0,
                        'path': node_path,
                        'is_leaf': False
                    }
                
                if i == len(parts) - 1:
                    current[part]['tokens'] += tokens
                    current[part]['files'] += files
                    current[part]['is_leaf'] = True
                    current[part]['path'] = directory
                
                if i < len(parts) - 1:
                    current = current[part]['children']
        
        # Calculate corrected totals
        def calculate_totals(node_dict: Dict):
            for name, data in node_dict.items():
                if data.get('children'):
                    calculate_totals(data['children'])
                    child_tokens = sum(child.get('tokens', 0) for child in data['children'].values())
                    child_files = sum(child.get('files', 0) for child in data['children'].values())
                    data['tokens'] = data.get('tokens', 0) + child_tokens
                    data['files'] = data.get('files', 0) + child_files
        
        calculate_totals(tree)
        
        # Extract corrected stats
        corrected_stats = extract_corrected_stats_from_tree(tree)
        
        # Create both structures for compatibility (now with corrected stats)
        flat_structure = create_flat_directory_structure(directory_stats, file_counts_by_dir, all_directories, corrected_stats)
        
        # Create directory structure based on user preference
        if use_tree:
            # Use the already created tree structure  
            directory_list = tree_structure
            
            # Optionally sort by tokens instead of hierarchy
            if sort_by_tokens:
                directory_list.sort(key=lambda x: (x[1]['is_empty'], -x[1]['tokens']))
        else:
            # Create flat structure (backward compatibility)
            directory_list = []
            
            # Sort by tokens (descending), but show empty directories at the end unless hidden
            sorted_dirs = sorted(flat_structure.items(), key=lambda x: (x[1]['tokens'] == 0, -x[1]['tokens']))
            
            for dir_name, dir_info in sorted_dirs:
                if not show_empty and dir_info['tokens'] == 0 and dir_info['files'] == 0:
                    continue
                directory_list.append((dir_name, dir_info))

        # Collect root files separately if using tree structure and showing files
        root_files_to_add = []
        if use_tree and args.files:
            # Find root files
            for file_path, ext in all_files:
                relative_path = os.path.relpath(file_path, analyze_path)
                file_dir_path = os.path.dirname(relative_path)
                file_directory = 'root' if file_dir_path in ('', '.') else file_dir_path
                
                if file_directory == 'root':
                    try:
                        content = read_file_with_encoding(file_path, config)
                        if content:
                            file_tokens = count_tokens(content)
                            filename = os.path.basename(relative_path)
                            file_percentage = (file_tokens / total_tokens) * 100
                            root_files_to_add.append((filename, file_tokens, file_percentage))
                    except:
                        continue
            
            # Sort root files by tokens
            root_files_to_add.sort(key=lambda x: x[1], reverse=True)

        # Add rows to directory table
        for dir_name, dir_info in directory_list:
            tokens = dir_info['tokens']
            files = dir_info['files']
            is_empty = dir_info.get('is_empty', tokens == 0 and files == 0)
            
            if tokens > 0:
                percentage = (tokens / total_tokens) * 100
                dir_table.add_row(
                    dir_name,
                    f"{format_number(tokens)}",
                    f"{percentage:.1f}%",
                    f"{files} files"
                )
            elif show_empty:
                # Empty directory (only show if show_empty is True)
                dir_table.add_row(
                    f"[dim]{dir_name}[/dim]",
                    "[dim]0[/dim]",
                    "[dim]0.0%[/dim]",
                    "[dim]0 files[/dim]"
                )
            
            # Show individual files if requested
            if args.files and tokens > 0:
                # For root directory in tree mode, skip adding files here - we'll add them at the end
                if use_tree and dir_info['path'] == 'root':
                    continue
                
                # Get files for this directory (non-root directories)
                directory_files = []
                for file_path, ext in all_files:
                    relative_path = os.path.relpath(file_path, analyze_path)
                    file_dir_path = os.path.dirname(relative_path)
                    file_directory = 'root' if file_dir_path in ('', '.') else file_dir_path
                    
                    # Match files to their exact directory
                    if file_directory == dir_info['path']:
                        try:
                            content = read_file_with_encoding(file_path, config)
                            if content:
                                file_tokens = count_tokens(content)
                                filename = os.path.basename(relative_path)
                                directory_files.append((filename, file_tokens))
                        except:
                            continue
                
                # Sort files by tokens and show top files
                directory_files.sort(key=lambda x: x[1], reverse=True)
                for filename, file_tokens in directory_files[:10]:  # Show top 10 files
                    file_percentage = (file_tokens / total_tokens) * 100
                    
                    # Adjust indentation based on structure type
                    if use_tree:
                        # Count indentation level from directory name
                        indent_count = (len(dir_name) - len(dir_name.lstrip())) // 2 + 1
                        file_prefix = "  " * indent_count + "📄 "
                    else:
                        # For flat structure, use simple indentation
                        file_prefix = "    📄 "
                    
                    dir_table.add_row(
                        f"{file_prefix}{filename}",
                        f"{format_number(file_tokens)}",
                        f"{file_percentage:.1f}%",
                        "1 file"
                    )
        
        # Add root files at the end for tree structure
        if use_tree and args.files and root_files_to_add:
            for filename, file_tokens, file_percentage in root_files_to_add[:10]:  # Show top 10 files
                dir_table.add_row(
                    f"  📄 {filename}",
                    f"{format_number(file_tokens)}",
                    f"{file_percentage:.1f}%",
                    "1 file"
                )

        console.print(dir_table)

        # Create individual file tokens table with configurable limit
        file_table = Table(title=f"\n[bold]Top {config.max_individual_files} Individual Files by Token Count[/bold]")
        file_table.add_column("File Path", style="cyan")
        file_table.add_column("Tokens", justify="right", style="green")
        file_table.add_column("Percentage", justify="right", style="yellow")

        # Calculate tokens for each file and sort by tokens
        file_tokens = []
        for file_path, ext in all_files:
            try:
                content = read_file_with_encoding(file_path, config)
                if content:
                    tokens = count_tokens(content)
                    relative_path = os.path.relpath(file_path, analyze_path)
                    file_tokens.append((relative_path, tokens))
            except:
                continue

        # Sort by tokens (descending) and show top files
        file_tokens.sort(key=lambda x: x[1], reverse=True)
        
        # Show configurable number of top files
        for file_path, tokens in file_tokens[:config.max_individual_files]:
            percentage = (tokens / total_tokens) * 100
            file_table.add_row(
                file_path,
                f"{format_number(tokens)}",
                f"{percentage:.1f}%"
            )

        console.print(file_table)

        context_table, fits_entirely = create_context_window_table(
            total_tokens, model_registry
        )
        console.print(context_table)

        # Show comprehensive strategies for fitting within context windows
        console.print(f"\n[bold yellow]🎯 Context Window Optimization Strategies[/bold yellow]")
        
        # Model recommendations
        if fits_entirely:
            console.print(f"\n[bold green]✅ Models that fit your entire codebase ({format_number(total_tokens)} tokens):[/bold green]")
            for model in fits_entirely[:5]:  # Show top 5
                console.print(f"  • [green]{model}[/green]")
        else:
            console.print(f"\n[yellow]⚠️  No models can fit the entire codebase ({format_number(total_tokens)} tokens)[/yellow]")
        
        # Size-based strategies
        if total_tokens > 500000:  # Very large codebase
            console.print(f"\n[bold red]🚨 LARGE CODEBASE STRATEGIES ({format_number(total_tokens)} tokens):[/bold red]")
            console.print(f"[red]Your codebase is quite large. Consider these approaches:[/red]")
            
            console.print(f"\n[cyan]🔄 Multi-Pass Analysis:[/cyan]")
            console.print(f"  • [white]Analyze core architecture first[/white] (entry points, configuration files)")
            console.print(f"  • [white]Then dive into specific modules[/white] (largest directories by token count)")
            console.print(f"  • [white]Finally review components[/white] (utilities, examples, documentation)")
            
            console.print(f"\n[cyan]📊 Modular Approach (Actual Directory Sizes):[/cyan]")
            # Show actual directory sizes from tree analysis (with corrected totals)
            if use_tree and directory_list:
                # Extract top directories from tree structure which has correct totals
                top_dirs = sorted([(dir_name.replace('📁 ', ''), dir_info['tokens']) 
                                 for dir_name, dir_info in directory_list if dir_info['tokens'] > 0], 
                                 key=lambda x: x[1], reverse=True)[:6]
            else:
                # Fallback to flat structure if tree not available
                top_dirs = sorted([(name.replace('📁 ', ''), info['tokens']) for name, info in flat_structure.items() if info['tokens'] > 0], 
                                 key=lambda x: x[1], reverse=True)[:6]
            for dir_name, tokens in top_dirs:
                percentage = (tokens / total_tokens) * 100
                console.print(f"  • [white]{dir_name}[/white]: {format_number(tokens)} tokens ({percentage:.1f}%)")
            
        elif total_tokens > 200000:  # Medium-large codebase
            console.print(f"\n[bold yellow]⚡ MEDIUM CODEBASE STRATEGIES ({format_number(total_tokens)} tokens):[/bold yellow]")
            
        if total_tokens > 100000:  # Any reasonably sized codebase
            console.print(f"\n[cyan]🛠️ Code Optimization (Apply in Order):[/cyan]")
            optimizations = [
                ("Remove extensive comments & docs", "20-30%", "Keep only essential comments"),
                ("Exclude examples/ directory", "10-15%", "Examples rarely needed for analysis"), 
                ("Remove debug/logging statements", "5-10%", "Focus on core logic"),
                ("Consolidate similar functions", "5-15%", "Merge duplicate patterns"),
                ("Minify variable names", "3-8%", "Last resort - hurts readability")
            ]
            
            for opt, saving, note in optimizations:
                estimated_savings = int(total_tokens * float(saving.split('-')[0]) / 100)
                console.print(f"  • [white]{opt}[/white] [green](save ~{saving}, ~{format_number(estimated_savings)} tokens)[/green]")
                console.print(f"    [dim]{note}[/dim]")
        
        # File prioritization
        console.print(f"\n[cyan]📂 File Priority for Analysis:[/cyan]")
        priorities = [
            ("🔥 Critical", ["entry points", "main configuration", "core modules"]),
            ("⚡ High", ["largest directories", "business logic", "core APIs"]),
            ("📊 Medium", ["utilities", "components", "integrations"]),
            ("📋 Low", ["examples", "documentation", "test files"])
        ]
        
        for priority, files in priorities:
            console.print(f"  {priority}: [white]{', '.join(files)}[/white]")
        
        # Add note about the -files option
        if not args.files:
            console.print(f"\n[yellow]💡 Tip: Use `-files` flag to see individual files within each directory![/yellow]")
        
        # Advanced chunking strategies  
        console.print(f"\n[cyan]🔀 Advanced Chunking Techniques:[/cyan]")
        console.print(f"  • [white]Dependency-based[/white]: Start with files that have no dependencies")
        console.print(f"  • [white]Feature-based[/white]: Group by functionality or domain")
        console.print(f"  • [white]Layer-based[/white]: Data → Logic → API → Presentation")
        console.print(f"  • [white]Size-based[/white]: Combine small files, split large ones")
        
        console.print(f"\n[bold green]💡 Pro Tip:[/bold green] [white]Start with essential files analysis, then expand based on findings![/white]")

    if temp_dir:
        shutil.rmtree(temp_dir)

def is_binary(file_path: str) -> bool:
    """Check if a file is binary."""
    try:
        with open(file_path, 'tr') as check_file:
            check_file.read(1024)
            return False
    except UnicodeDecodeError:
        return True

def count_tokens(content: str) -> int:
    """Count tokens in the given content using GPT-2 tokenizer."""
    return len(tokenizer.encode(content))

def format_number(num: int) -> str:
    """Format a number with thousands separator and appropriate suffix."""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    return f"{num:,}"

if __name__ == "__main__":
    main()
