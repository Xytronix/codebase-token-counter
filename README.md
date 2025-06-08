# Code Token Counter

[![PyPI version](https://badge.fury.io/py/codebase-token-counter.svg)](https://badge.fury.io/py/codebase-token-counter)
[![Test](https://github.com/liatrio/codebase-token-counter/actions/workflows/test.yml/badge.svg)](https://github.com/liatrio/codebase-token-counter/actions/workflows/test.yml)

A comprehensive tool for analyzing codebases to understand their token usage and compatibility with various Large Language Models (LLMs). This tool helps developers understand if their code can fit within different LLM context windows, how tokens are distributed across technologies, and provides detailed optimization strategies.

## Features

### Core Analysis
- **Local & Remote Analysis**: Analyze both local directories and remote Git repositories
- **Smart File Detection**: Automatically detects and processes text-based files while ignoring binaries
- **Intelligent Encoding**: Advanced encoding detection with fallback support for various file formats
- **Technology Categorization**: Groups files by their technology/language with support for 100+ file types

### Advanced Display Options
- **Tree Structure**: Hierarchical directory view showing nested relationships
- **Flat Structure**: Simple list view for quick scanning
- **Individual File Analysis**: Show top files within each directory
- **Flexible Sorting**: Sort by hierarchy or token count
- **Empty Directory Handling**: Show or hide empty directories

### LLM Context Window Analysis
- **Comprehensive LLM Database**: Automatically updated pricing and context window data from LiteLLM
- **Popular Models Supported**:
  - **OpenAI**: GPT-4o, GPT-4.1, o1, o3, o4 series
  - **Anthropic**: Claude 3.5 Sonnet/Haiku, Claude 4 series
  - **Google**: Gemini 1.5/2.0/2.5 Pro/Flash, Gemini Exp
  - **xAI**: Grok 2, Grok 3 series
  - **Meta**: Llama 4 Scout/Maverick
  - **DeepSeek**: Chat, Coder, Reasoner models
  - **Mistral**: Large, Medium, Devstral models
- **Usage Analysis**: Shows percentage of context window used and fit status
- **Optimization Strategies**: Provides actionable recommendations for large codebases

### Intelligent Exclusions
- **Smart Defaults**: Automatically excludes common non-source directories (venv, .git, node_modules, etc.)
- **Custom Exclusions**: Configure directories, files, and extensions to exclude
- **Pattern Matching**: Support for file pattern exclusions

## Installation

### Using uv (Recommended)

The script includes inline dependencies, so you can run it directly with uv:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run the script directly (no virtual environment needed)
uv run codebase_token_counter/token_counter.py <path_or_repo>
```

### Using pip

```bash
pip install codebase-token-counter
```

Or install from source:

```bash
# Clone the repository
git clone https://github.com/liatrio/codebase-token-counter.git
cd codebase-token-counter

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Analyze local directory
token-counter /path/to/your/codebase

# Analyze remote repository
token-counter https://github.com/username/repo.git

# Using uv with the script directly
uv run codebase_token_counter/token_counter.py .
```

### Advanced Usage

```bash
# Get only total token count (useful for scripts)
token-counter . --total

# Show individual files within directories
token-counter . --files

# Enable debug output for troubleshooting
token-counter . --debug

# Custom exclusions
token-counter . --exclude-dirs "build,dist,docs" --exclude-files "*.test.*,*.spec.*"

# Force specific encoding
token-counter . --encoding utf-8

# Flat directory structure sorted by tokens
token-counter . --flat --sort-by-tokens --hide-empty

# Limit individual file display
token-counter . --files --max-files 20
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--total`, `-t` | Only output the total token count (no tables) |
| `--debug`, `-d` | Enable debug output showing file processing |
| `--files`, `-f` | Show individual files within directories |
| `--exclude-dirs` | Comma-separated list of directories to exclude |
| `--exclude-files` | Comma-separated list of file patterns to exclude |
| `--exclude-extensions` | Comma-separated list of extensions to exclude |
| `--encoding` | Force specific encoding (utf-8, latin1, cp1252, etc.) |
| `--fallback-encodings` | Comma-separated fallback encodings to try |
| `--max-files` | Maximum number of individual files to show (default: 50) |
| `--tree` | Show directory structure as tree (default) |
| `--flat` | Show directory structure as flat list |
| `--show-empty` | Show empty directories (default) |
| `--hide-empty` | Hide empty directories |
| `--sort-by-tokens` | Sort directories by token count instead of hierarchy |

## Output

The tool provides comprehensive analysis in multiple sections:

### 1. Extension Breakdown
Shows tokens and file counts grouped by file extension.

### 2. Technology Distribution
Groups files by programming language/technology (Python, JavaScript, etc.).

### 3. Directory Analysis
- **Tree View**: Hierarchical structure showing parent-child relationships
- **Flat View**: Simple list sorted by token count
- **File Details**: Individual file breakdown when using `--files`

### 4. Context Window Analysis
Compares your codebase size against popular LLM context windows, showing:
- Input/output token limits
- Usage percentage
- Fit status (✅ Fits, ⚠️ Tight, ❌ Too Big)

### 5. Optimization Strategies
For large codebases, provides specific recommendations:
- Multi-pass analysis approaches
- Code optimization techniques
- File prioritization strategies
- Advanced chunking methods

## Automated Updates

This project includes automated GitHub workflows:

### 🔄 LLM Pricing Data Updates (`llm-pricing.yml`)
- **Trigger**: Every 4 hours, on releases, or manual dispatch
- **Purpose**: Automatically downloads and converts the latest LiteLLM pricing data
- **Output**: Updates `llm_pricing_data.json` with current model pricing and context windows
- **Smart Updates**: Only processes when LiteLLM data actually changes

### 🧪 Testing (`test.yml`)
- **Trigger**: Push to main, pull requests
- **Purpose**: Runs comprehensive tests across Python 3.8-3.11
- **Coverage**: Includes installation testing and package building

### 📦 Publishing (`publish.yml`)
- **Trigger**: Version tags (v*)
- **Purpose**: Automatically publishes to PyPI after successful tests
- **Security**: Uses trusted publishing with OpenID Connect

## Supported File Types

The tool supports 100+ file types across multiple categories:

- **Programming Languages**: Python, JavaScript, TypeScript, Java, C/C++, Rust, Go, Swift, Kotlin, etc.
- **Web Technologies**: HTML, CSS, SCSS, Vue, React, Angular, Astro, etc.
- **Documentation**: Markdown, reStructuredText, LaTeX, AsciiDoc
- **Configuration**: YAML, TOML, JSON, INI, environment files
- **Data Formats**: CSV, TSV, XML, Protocol Buffers
- **Specialized**: Jupyter Notebooks, Docker files, CMake, Gradle

## Example Output

```text
Results:
Total tokens: 15.2K (15,234)

      Tokens by file extension
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Extension ┃       Tokens ┃  Files ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━┩
│ .py       │ 12.1K (12,108) │ 15 files │
│ .md       │ 2.8K (2,834) │ 8 files │
│ .yml      │   292 (292) │ 3 files │
└───────────┴──────────────┴────────┘

         Tokens by Technology
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Technology ┃       Tokens ┃  Files ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Python     │ 12.1K (12,108) │ 15 files │
│ Markdown   │ 2.8K (2,834) │ 8 files │
│ YAML       │   292 (292) │ 3 files │
└────────────┴──────────────┴────────┘

        Context Window Comparisons
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Model                  ┃ Input Limit   ┃ Input Usage   ┃ Status        ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ GPT-4o                 │       128K    │          11.9%│ ✅ Fits      │
│ Claude 3.5 Sonnet      │       200K    │           7.6%│ ✅ Fits      │
│ Gemini 1.5 Pro         │     2.0M      │           0.8%│ ✅ Fits      │
│ o1                     │       200K    │           7.6%│ ✅ Fits      │
└────────────────────────┴───────────────┴───────────────┴───────────────┘

🎯 Context Window Optimization Strategies

✅ Models that fit your entire codebase (15.2K tokens):
  • GPT-4o
  • Claude 3.5 Sonnet
  • Gemini 1.5 Pro
  • o1

💡 Pro Tip: Start with essential files analysis, then expand based on findings!
```

## Contributing

Contributions are welcome! Areas for improvement:

- **File Type Support**: Add new programming languages and frameworks
- **LLM Coverage**: Include additional model providers
- **Analysis Features**: Enhanced token counting accuracy and performance
- **Output Formats**: JSON, CSV, or other structured outputs
- **Integration**: IDE plugins or CI/CD integrations

## Development

```bash
# Setup development environment
git clone https://github.com/liatrio/codebase-token-counter.git
cd codebase-token-counter
pip install -e .

# Run tests
pytest

# Run with development version
python codebase_token_counter/token_counter.py .
```

## License

MIT License - Feel free to use and modify as needed.
