# Code Token Counter

[![PyPI version](https://badge.fury.io/py/code-token-counter.svg)](https://badge.fury.io/py/code-token-counter)
[![Test](https://github.com/Xytronix/codebase-token-counter/actions/workflows/ci.yml/badge.svg)](https://github.com/Xytronix/codebase-token-counter/actions/workflows/ci.yml)

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

- **Bundled Model Registry**: Reproducible context-window data that works independently of the repository being analyzed
- **Popular Models Supported**:
  - **OpenAI**: GPT-6 Astra and GPT-5.6 Sol/Terra/Luna
  - **Anthropic**: Claude Fable 5.1, Opus 5, Sonnet 5, and Haiku 4.5
  - **Google**: Gemini 3.8 Flash, 3.5 Flash-Lite, and 2.5 Pro
  - **xAI**: Grok 4.6
  - **Meta**: Llama 4 Scout/Maverick
  - **DeepSeek**: DeepSeek V4 Pro/Flash
  - **Mistral**: Mistral Large/Medium and Devstral/Devstral Small
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
git clone https://github.com/Xytronix/codebase-token-counter.git
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

- **Trigger**: Daily, on releases, or manual dispatch
- **Purpose**: Downloads and converts the full LiteLLM pricing dataset for publication
- **Output**: Updates the separate `llm_pricing_data.json` pricing artifact; runtime context comparisons use the bundled registry instead
- **Smart Updates**: Only processes when LiteLLM data actually changes

The bundled context-window registry is a curated snapshot of LiteLLM commit
[`3d0fd127`](https://github.com/BerriAI/litellm/commit/3d0fd127d5a151f7f094462b16ac9c2a01a047b6)
from 2026-09-17. The selected families and limits were cross-checked against the
[OpenAI](https://developers.openai.com/api/docs/models),
[Anthropic](https://platform.claude.com/docs/en/models/overview),
[Google](https://ai.google.dev/gemini-api/docs/models),
[xAI](https://docs.x.ai/developers/models/grok-4.6),
[DeepSeek](https://api-docs.deepseek.com/updates/),
[Meta](https://ai.meta.com/llama/get-started/), and
[Mistral](https://mistral.ai/models/) model documentation. LiteLLM's normalized
input and output limits are used when a provider documents only a combined
context window.

### 🧪 CI/CD Pipeline (`ci.yml`)

- **Trigger**: Push to main, pull requests, version tags (v*)
- **Purpose**: Runs comprehensive tests across Python 3.8-3.11, builds packages, and publishes to PyPI on releases
- **Coverage**: Includes installation testing and package building
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

<details>
<summary>🔍 Click to view detailed analysis output</summary>

```text
Analyzing local directory: .
Processing files ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:01

Results:
Total tokens: 1.4M (1,364,450)
                                  
     Tokens by file extension     
┏━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┓
┃ Extension ┃ Tokens ┃     Files ┃
┡━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━┩
│ .lua      │   1.3M │ 153 files │
│ .md       │ 62,631 │   7 files │
└───────────┴────────┴───────────┘
                                   
       Tokens by Technology        
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┓
┃ Technology ┃ Tokens ┃     Files ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━┩
│ Lua        │   1.3M │ 153 files │
│ Markdown   │ 62,631 │   7 files │
└────────────┴────────┴───────────┘
                                                                                   
                       Tokens by Directory (Tree Structure)                        
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Directory                                    ┃  Tokens ┃ Percentage ┃     Files ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 📁 assistant.koplugin                        │    1.4M │     100.0% │ 160 files │
│   📁 utils                                   │ 613,983 │      45.0% │  87 files │
│     📁 ai                                    │ 206,927 │      15.2% │  20 files │
│       📁 services                            │ 136,542 │      10.0% │   4 files │
│         📄 tts_service.lua                   │ 100,291 │       7.4% │    1 file │
│         📄 model_discovery_service.lua       │  23,758 │       1.7% │    1 file │
│         📄 device_audio_integrator.lua       │   7,565 │       0.6% │    1 file │
│         📄 live_search_service.lua           │   4,928 │       0.4% │    1 file │
│       📁 execution                           │  47,432 │       3.5% │  10 files │
│         📄 highlight_processor.lua           │   8,044 │       0.6% │    1 file │
│         📄 query_handler.lua                 │   7,912 │       0.6% │    1 file │
│         📄 query_orchestrator.lua            │   7,224 │       0.5% │    1 file │
│         📄 response_processor.lua            │   5,354 │       0.4% │    1 file │
│         📄 common_utilities.lua              │   4,911 │       0.4% │    1 file │
│         📄 tool_execution_handler.lua        │   3,326 │       0.2% │    1 file │
│         📄 error_handler.lua                 │   3,218 │       0.2% │    1 file │
│         📄 cost_tracker.lua                  │   3,043 │       0.2% │    1 file │
│         📄 summarization_engine.lua          │   2,448 │       0.2% │    1 file │
│         📄 request_manager.lua               │   1,952 │       0.1% │    1 file │
│       📁 tools                               │  12,632 │       0.9% │   3 files │
│         📄 tool_caller.lua                   │   8,887 │       0.7% │    1 file │
│         📄 tool_registration_helper.lua      │   2,403 │       0.2% │    1 file │
│         📄 tool_helpers.lua                  │   1,342 │       0.1% │    1 file │
│       📁 processors                          │   7,863 │       0.6% │   2 files │
│         📄 book_analyzer.lua                 │   4,454 │       0.3% │    1 file │
│         📄 smart_context_manager.lua         │   3,409 │       0.2% │    1 file │
│       📁 generators                          │   2,458 │       0.2% │   1 files │
│         📄 topic_generator.lua               │   2,458 │       0.2% │    1 file │
│     📁 core                                  │  88,057 │       6.5% │  14 files │
│       📁 networking                          │  29,656 │       2.2% │   4 files │
│         📄 mcp_client.lua                    │  11,916 │       0.9% │    1 file │
│         📄 network_helper.lua                │   9,046 │       0.7% │    1 file │
│         📄 mcp_bridge_client.lua             │   5,267 │       0.4% │    1 file │
│         📄 auto_wifi_manager.lua             │   3,427 │       0.3% │    1 file │
│       📁 validation                          │  23,807 │       1.7% │   2 files │
│         📄 config_validator.lua              │  12,962 │       0.9% │    1 file │
│         📄 validation_handler.lua            │  10,845 │       0.8% │    1 file │
│       📁 data                                │  19,733 │       1.4% │   3 files │
│         📄 core_utilities.lua                │  11,385 │       0.8% │    1 file │
│         📄 json_utils.lua                    │   5,567 │       0.4% │    1 file │
│         📄 file_format_utilities.lua         │   2,781 │       0.2% │    1 file │
│       📁 utilities                           │  14,861 │       1.1% │   5 files │
│         📄 validation_helper.lua             │   4,004 │       0.3% │    1 file │
│         📄 cleanup_coordinator.lua           │   3,949 │       0.3% │    1 file │
│         📄 cache_manager.lua                 │   3,649 │       0.3% │    1 file │
│         📄 timer_utils.lua                   │   2,395 │       0.2% │    1 file │
│         📄 request_deduplicator.lua          │     864 │       0.1% │    1 file │
│     📁 management                            │  85,577 │       6.3% │  16 files │
│       📁 automation                          │  47,363 │       3.5% │  11 files │
│         📄 export_handler.lua                │  10,726 │       0.8% │    1 file │
│         📄 pipeline_manager.lua              │   5,571 │       0.4% │    1 file │
│         📄 background_llm_service.lua        │   5,289 │       0.4% │    1 file │
│         📄 trigger_engine.lua                │   5,017 │       0.4% │    1 file │
│         📄 task_scheduler.lua                │   4,899 │       0.4% │    1 file │
│         📄 background_llm_automation.lua     │   4,804 │       0.4% │    1 file │
│         📄 highlight_handler.lua             │   4,218 │       0.3% │    1 file │
│         📄 translation_handler.lua           │   3,895 │       0.3% │    1 file │
│         📄 task_storage.lua                  │   1,525 │       0.1% │    1 file │
│         📄 automation_manager.lua            │   1,087 │       0.1% │    1 file │
│       📁 config                              │  24,531 │       1.8% │   3 files │
│         📄 config_service.lua                │  11,411 │       0.8% │    1 file │
│         📄 template_manager.lua              │   9,652 │       0.7% │    1 file │
│         📄 checkpoint_manager.lua            │   3,468 │       0.3% │    1 file │
│       📁 integration                         │  13,683 │       1.0% │   2 files │
│         📄 mcp_manager.lua                   │   8,467 │       0.6% │    1 file │
│         📄 integration_manager.lua           │   5,216 │       0.4% │    1 file │
│     📁 api                                   │  71,070 │       5.2% │  18 files │
│       📄 rate_limiter.lua                    │   2,168 │       0.2% │    1 file │
│       📁 files                               │   5,643 │       0.4% │   2 files │
│         📄 files_manager.lua                 │   4,590 │       0.3% │    1 file │
│         📁 providers                         │   1,053 │       0.1% │   1 files │
│           📄 base_adapter.lua                │   1,053 │       0.1% │    1 file │
│       📁 providers                           │  22,634 │       1.7% │   6 files │
│         📄 provider_capabilities.lua         │   5,580 │       0.4% │    1 file │
│         📄 provider_registry.lua             │   4,365 │       0.3% │    1 file │
│         📄 provider_manager.lua              │   3,583 │       0.3% │    1 file │
│         📄 provider_lifecycle.lua            │   3,086 │       0.2% │    1 file │
│         📄 provider_config_manager.lua       │   3,060 │       0.2% │    1 file │
│         📄 provider_prompt_manager.lua       │   2,960 │       0.2% │    1 file │
│       📁 formatters                          │  13,356 │       1.0% │   3 files │
│         📄 tool_formatter.lua                │   5,031 │       0.4% │    1 file │
│         📄 format_conversion.lua             │   4,719 │       0.3% │    1 file │
│         📄 message_formatter.lua             │   3,606 │       0.3% │    1 file │
│       📁 processors                          │  12,910 │       0.9% │   4 files │
│         📄 context_placeholder_processor.lua │   3,490 │       0.3% │    1 file │
│         📄 context_template_engine.lua       │   3,466 │       0.3% │    1 file │
│         📄 context_fingerprint_manager.lua   │   3,428 │       0.3% │    1 file │
│         📄 context_processor.lua             │   2,526 │       0.2% │    1 file │
│       📁 payloads                            │   8,478 │       0.6% │   1 files │
│         📄 payload_builder.lua               │   8,478 │       0.6% │    1 file │
│       📁 parsers                             │   5,881 │       0.4% │   1 files │
│         📄 response_parser.lua               │   5,881 │       0.4% │    1 file │
│     📁 ui                                    │  67,544 │       5.0% │   8 files │
│       📁 services                            │  36,818 │       2.7% │   1 files │
│         📄 dialog_service.lua                │  36,818 │       2.7% │    1 file │
│       📁 helpers                             │  19,124 │       1.4% │   4 files │
│         📄 context_helper.lua                │   6,358 │       0.5% │    1 file │
│         📄 ui_helpers.lua                    │   4,669 │       0.3% │    1 file │
│         📄 template_ui_helper.lua            │   4,319 │       0.3% │    1 file │
│         📄 title_template_engine.lua         │   3,778 │       0.3% │    1 file │
│       📁 components                          │  11,602 │       0.9% │   3 files │
│         📄 tts_response_widget.lua           │   5,774 │       0.4% │    1 file │
│         📄 runtime_translations.lua          │   4,038 │       0.3% │    1 file │
│         📄 tts_button.lua                    │   1,790 │       0.1% │    1 file │
│     📁 storage                               │  59,812 │       4.4% │   7 files │
│       📁 database                            │  37,350 │       2.7% │   5 files │
│         📄 conversation_storage.lua          │  12,979 │       1.0% │    1 file │
│         📄 cost_storage.lua                  │  12,069 │       0.9% │    1 file │
│         📄 db_migration.lua                  │   6,706 │       0.5% │    1 file │
│         📄 history_db.lua                    │   3,034 │       0.2% │    1 file │
│         📄 db_connection.lua                 │   2,562 │       0.2% │    1 file │
│       📁 cache                               │  22,462 │       1.6% │   2 files │
│         📄 pricing_calculator.lua            │  19,039 │       1.4% │    1 file │
│         📄 response_cache.lua                │   3,423 │       0.3% │    1 file │
│     📁 infrastructure                        │  34,996 │       2.6% │   4 files │
│       📁 logging                             │  21,236 │       1.6% │   2 files │
│         📄 error_recovery.lua                │  13,382 │       1.0% │    1 file │
│         📄 logger_helper.lua                 │   7,854 │       0.6% │    1 file │
│       📁 updates                             │   7,136 │       0.5% │   1 files │
│         📄 update_checker.lua                │   7,136 │       0.5% │    1 file │
│       📁 events                              │   6,624 │       0.5% │   1 files │
│         📄 events.lua                        │   6,624 │       0.5% │    1 file │
│   📁 tools                                   │ 262,306 │      19.2% │  23 files │
│     📁 reader                                │ 117,685 │       8.6% │   5 files │
│       📄 navigation_tools.lua                │  67,857 │       5.0% │    1 file │
│       📄 annotation_tools.lua                │  17,303 │       1.3% │    1 file │
│       📄 tts_tools.lua                       │  16,002 │       1.2% │    1 file │
│       📄 document_tools.lua                  │  10,301 │       0.8% │    1 file │
│       📄 search_tools.lua                    │   6,222 │       0.5% │    1 file │
│     📁 integration                           │  65,778 │       4.8% │   7 files │
│       📄 email_tools.lua                     │  20,706 │       1.5% │    1 file │
│       📄 pipeline_tools.lua                  │  12,611 │       0.9% │    1 file │
│       📄 background_llm_tools.lua            │   9,504 │       0.7% │    1 file │
│       📄 automated_tasks_tools.lua           │   8,852 │       0.6% │    1 file │
│       📄 data_management_tools.lua           │   6,290 │       0.5% │    1 file │
│       📄 flashcard_tools.lua                 │   4,365 │       0.3% │    1 file │
│       📄 wallabag_tools.lua                  │   3,450 │       0.3% │    1 file │
│     📁 library                               │  28,434 │       2.1% │   4 files │
│       📄 hardcover_tools.lua                 │   8,962 │       0.7% │    1 file │
│       📄 library_discovery_tools.lua         │   8,894 │       0.7% │    1 file │
│       📄 google_books_tools.lua              │   5,301 │       0.4% │    1 file │
│       📄 openlibrary_tools.lua               │   5,277 │       0.4% │    1 file │
│     📁 web                                   │  26,924 │       2.0% │   3 files │
│       📄 content_tools.lua                   │   9,281 │       0.7% │    1 file │
│       📄 search_tools.lua                    │   9,008 │       0.7% │    1 file │
│       📄 serpapi_tools.lua                   │   8,635 │       0.6% │    1 file │
│     📁 device                                │  23,485 │       1.7% │   4 files │
│       📄 filesystem_tools.lua                │   7,216 │       0.5% │    1 file │
│       📄 settings_tools.lua                  │   6,142 │       0.5% │    1 file │
│       📄 document_management_tools.lua       │   5,859 │       0.4% │    1 file │
│       📄 device_status_and_control_tools.lua │   4,268 │       0.3% │    1 file │
│   📁 api_handlers                            │ 135,873 │      10.0% │  24 files │
│     📄 google.lua                            │  10,473 │       0.8% │    1 file │
│     📄 litellm.lua                           │   9,957 │       0.7% │    1 file │
│     📄 base.lua                              │   9,776 │       0.7% │    1 file │
│     📄 azure.lua                             │   6,246 │       0.5% │    1 file │
│     📄 perplexity.lua                        │   5,851 │       0.4% │    1 file │
│     📄 xai.lua                               │   5,645 │       0.4% │    1 file │
│     📄 anthropic.lua                         │   5,414 │       0.4% │    1 file │
│     📄 alibaba.lua                           │   5,360 │       0.4% │    1 file │
│     📄 openai.lua                            │   4,946 │       0.4% │    1 file │
│     📄 cohere.lua                            │   4,835 │       0.4% │    1 file │
│     📁 helpers                               │  34,619 │       2.5% │   3 files │
│       📄 openai_chat.lua                     │  19,569 │       1.4% │    1 file │
│       📄 anthropic_messages.lua              │  12,206 │       0.9% │    1 file │
│       📄 format_converters.lua               │   2,844 │       0.2% │    1 file │
│   📁 components                              │  36,966 │       2.7% │   5 files │
│     📁 documents                             │  36,966 │       2.7% │   5 files │
│       📄 document_manager.lua                │   3,124 │       0.2% │    1 file │
│       📁 builders                            │  33,842 │       2.5% │   4 files │
│         📄 tts_ui_builder.lua                │  23,930 │       1.8% │    1 file │
│         📄 html_builder.lua                  │   4,660 │       0.3% │    1 file │
│         📄 rtf_builder.lua                   │   2,636 │       0.2% │    1 file │
│         📄 markdown_builder.lua              │   2,616 │       0.2% │    1 file │
│   📁 examples                                │  32,900 │       2.4% │   7 files │
│     📄 litellm_comprehensive_example.lua     │   7,883 │       0.6% │    1 file │
│     📄 integration_examples.lua              │   6,497 │       0.5% │    1 file │
│     📄 mcp_integration_example.lua           │   5,494 │       0.4% │    1 file │
│     📄 test_mcp_bridge.lua                   │   4,041 │       0.3% │    1 file │
│     📄 dynamic_event_hookup_examples.lua     │   3,630 │       0.3% │    1 file │
│     📄 automation_event_examples.lua         │   3,078 │       0.2% │    1 file │
│     📄 network_caching_example.lua           │   2,277 │       0.2% │    1 file │
│   📄 llm_viewer.lua                          │  60,890 │       4.5% │    1 file │
│   📄 configuration.lua                       │  44,619 │       3.3% │    1 file │
│   📄 assistant_browser.lua                   │  40,053 │       2.9% │    1 file │
│   📄 README.md                               │  34,901 │       2.6% │    1 file │
│   📄 menu_builder.lua                        │  30,474 │       2.2% │    1 file │
│   📄 configuration.lua.sample                │  25,134 │       1.8% │    1 file │
│   📄 main.lua                                │  18,470 │       1.4% │    1 file │
│   📄 DEVELOPER-MANUAL.md                     │  13,891 │       1.0% │    1 file │
│   📄 USER-MANUAL.md                          │   4,795 │       0.4% │    1 file │
│   📄 Changelog.md                            │   2,326 │       0.2% │    1 file │
└──────────────────────────────────────────────┴─────────┴────────────┴───────────┘
                                                                           
                  Top 50 Individual Files by Token Count                   
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ File Path                                        ┃  Tokens ┃ Percentage ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ utils/ai/services/tts_service.lua                │ 100,291 │       7.4% │
│ tools/reader/navigation_tools.lua                │  67,857 │       5.0% │
│ llm_viewer.lua                                   │  60,890 │       4.5% │
│ configuration.lua                                │  44,619 │       3.3% │
│ assistant_browser.lua                            │  40,053 │       2.9% │
│ utils/ui/services/dialog_service.lua             │  36,818 │       2.7% │
│ README.md                                        │  34,901 │       2.6% │
│ menu_builder.lua                                 │  30,474 │       2.2% │
│ configuration.lua.sample                         │  25,134 │       1.8% │
│ components/documents/builders/tts_ui_builder.lua │  23,930 │       1.8% │
│ utils/ai/services/model_discovery_service.lua    │  23,758 │       1.7% │
│ tools/integration/email_tools.lua                │  20,706 │       1.5% │
│ api_handlers/helpers/openai_chat.lua             │  19,569 │       1.4% │
│ utils/storage/cache/pricing_calculator.lua       │  19,039 │       1.4% │
│ main.lua                                         │  18,470 │       1.4% │
│ tools/reader/annotation_tools.lua                │  17,303 │       1.3% │
│ tools/reader/tts_tools.lua                       │  16,002 │       1.2% │
│ DEVELOPER-MANUAL.md                              │  13,891 │       1.0% │
│ utils/infrastructure/logging/error_recovery.lua  │  13,382 │       1.0% │
│ utils/storage/database/conversation_storage.lua  │  12,979 │       1.0% │
│ utils/core/validation/config_validator.lua       │  12,962 │       0.9% │
│ tools/integration/pipeline_tools.lua             │  12,611 │       0.9% │
│ api_handlers/helpers/anthropic_messages.lua      │  12,206 │       0.9% │
│ utils/storage/database/cost_storage.lua          │  12,069 │       0.9% │
│ utils/core/networking/mcp_client.lua             │  11,916 │       0.9% │
│ utils/management/config/config_service.lua       │  11,411 │       0.8% │
│ utils/core/data/core_utilities.lua               │  11,385 │       0.8% │
│ utils/core/validation/validation_handler.lua     │  10,845 │       0.8% │
│ utils/management/automation/export_handler.lua   │  10,726 │       0.8% │
│ api_handlers/google.lua                          │  10,473 │       0.8% │
│ tools/reader/document_tools.lua                  │  10,301 │       0.8% │
│ api_handlers/litellm.lua                         │   9,957 │       0.7% │
│ api_handlers/base.lua                            │   9,776 │       0.7% │
│ utils/management/config/template_manager.lua     │   9,652 │       0.7% │
│ tools/integration/background_llm_tools.lua       │   9,504 │       0.7% │
│ tools/web/content_tools.lua                      │   9,281 │       0.7% │
│ utils/core/networking/network_helper.lua         │   9,046 │       0.7% │
│ tools/web/search_tools.lua                       │   9,008 │       0.7% │
│ tools/library/hardcover_tools.lua                │   8,962 │       0.7% │
│ tools/library/library_discovery_tools.lua        │   8,894 │       0.7% │
│ utils/ai/tools/tool_caller.lua                   │   8,887 │       0.7% │
│ tools/integration/automated_tasks_tools.lua      │   8,852 │       0.6% │
│ tools/web/serpapi_tools.lua                      │   8,635 │       0.6% │
│ utils/api/payloads/payload_builder.lua           │   8,478 │       0.6% │
│ utils/management/integration/mcp_manager.lua     │   8,467 │       0.6% │
│ utils/ai/execution/highlight_processor.lua       │   8,044 │       0.6% │
│ utils/ai/execution/query_handler.lua             │   7,912 │       0.6% │
│ examples/litellm_comprehensive_example.lua       │   7,883 │       0.6% │
│ utils/infrastructure/logging/logger_helper.lua   │   7,854 │       0.6% │
│ utils/ai/services/device_audio_integrator.lua    │   7,565 │       0.6% │
└──────────────────────────────────────────────────┴─────────┴────────────┘
                                                                               
                            Context Window Comparisons
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Model                   ┃ Input Limit ┃ Input Usage ┃ Output Limit ┃   Status   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Anthropic               │             │             │              │            │
│   Claude Fable 5.1      │        1.0M │      136.4% │         128K │  ⚠️  Tight  │
│   Claude Opus 5         │        1.0M │      136.4% │         128K │  ⚠️  Tight  │
│   Claude Sonnet 5       │        1.0M │      136.4% │         128K │  ⚠️  Tight  │
│   Claude Haiku 4.5      │        200K │      682.2% │          64K │ ❌ Too Big │
│ OpenAI                  │             │             │              │            │
│   GPT-6 Astra           │        922K │      148.0% │         128K │  ⚠️  Tight  │
│   GPT-5.6 Sol           │        922K │      148.0% │         128K │  ⚠️  Tight  │
│   GPT-5.6 Terra         │        922K │      148.0% │         128K │  ⚠️  Tight  │
│   GPT-5.6 Luna          │        922K │      148.0% │         128K │  ⚠️  Tight  │
│ Google                  │             │             │              │            │
│   Gemini 3.8 Flash      │        1.0M │      130.1% │          66K │  ⚠️  Tight  │
│   Gemini 3.5 Flash-Lite │        1.0M │      130.1% │          66K │  ⚠️  Tight  │
│   Gemini 2.5 Pro        │        1.0M │      130.1% │          66K │  ⚠️  Tight  │
│ xAI                     │             │             │              │            │
│   Grok 4.6              │        500K │      272.9% │         500K │ ❌ Too Big │
│ Meta                    │             │             │              │            │
│   Llama 4 Scout         │       10.0M │       13.6% │           4K │  ✅ Fits   │
│   Llama 4 Maverick      │        1.0M │      136.4% │           4K │  ⚠️  Tight  │
│ DeepSeek                │             │             │              │            │
│   DeepSeek V4 Pro       │        1.0M │      136.4% │         393K │  ⚠️  Tight  │
│   DeepSeek V4 Flash     │        1.0M │      136.4% │         393K │  ⚠️  Tight  │
│ Mistral                 │             │             │              │            │
│   Mistral Large         │        262K │      520.5% │         262K │ ❌ Too Big │
│   Mistral Medium        │        262K │      520.5% │         262K │ ❌ Too Big │
│   Devstral              │        256K │      533.0% │         256K │ ❌ Too Big │
│   Devstral Small        │        256K │      533.0% │         256K │ ❌ Too Big │
└─────────────────────────┴─────────────┴─────────────┴──────────────┴────────────┘

🎯 Context Window Optimization Strategies

✅ Models that fit your entire codebase (1.4M tokens):
  • Llama 4 Scout

🚨 LARGE CODEBASE STRATEGIES (1.4M tokens):
Your codebase is quite large. Consider these approaches:

🔄 Multi-Pass Analysis:
  • Analyze core architecture first (entry points, configuration files)
  • Then dive into specific modules (largest directories by token count)
  • Finally review components (utilities, examples, documentation)

📊 Modular Approach (Actual Directory Sizes):
  • assistant.koplugin: 1.4M tokens (100.0%)
  •   utils: 613,983 tokens (45.0%)
  •   tools: 262,306 tokens (19.2%)
  •     ai: 206,927 tokens (15.2%)
  •       services: 136,542 tokens (10.0%)
  •   api_handlers: 135,873 tokens (10.0%)

🛠️ Code Optimization (Apply in Order):
  • Remove extensive comments & docs (save ~20-30%, ~272,890 tokens)
    Keep only essential comments
  • Exclude examples/ directory (save ~10-15%, ~136,445 tokens)
    Examples rarely needed for analysis
  • Remove debug/logging statements (save ~5-10%, ~68,222 tokens)
    Focus on core logic
  • Consolidate similar functions (save ~5-15%, ~68,222 tokens)
    Merge duplicate patterns
  • Minify variable names (save ~3-8%, ~40,933 tokens)
    Last resort - hurts readability

📂 File Priority for Analysis:
  🔥 Critical: entry points, main configuration, core modules
  ⚡ High: largest directories, business logic, core APIs
  📊 Medium: utilities, components, integrations
  📋 Low: examples, documentation, test files

🔀 Advanced Chunking Techniques:
  • Dependency-based: Start with files that have no dependencies
  • Feature-based: Group by functionality or domain
  • Layer-based: Data → Logic → API → Presentation
  • Size-based: Combine small files, split large ones

💡 Pro Tip: Start with essential files analysis, then expand based on findings!
```

</details>

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
git clone https://github.com/Xytronix/codebase-token-counter.git
cd codebase-token-counter
pip install -e .

# Run tests
pytest

# Run with development version
python codebase_token_counter/token_counter.py .
```

## License

MIT License - Feel free to use and modify as needed.
