  ```ascii

  ██▀███   ▄▄▄            ▄▄▄       ██▓▓█████▄ 
 ▓██ ▒ ██▒▒████▄         ▒████▄    ▓██▒▒██▀ ██▌
 ▓██ ░▄█ ▒▒██  ▀█▄       ▒██  ▀█▄  ▒██▒░██   █▌
 ▒██▀▀█▄  ░██▄▄▄▄██      ░██▄▄▄▄██ ░██░░▓█▄   ▌
 ░██▓ ▒██▒ ▓█   ▓██▒ ██▓  ▓█   ▓██▒░██░░▒████▓ 
 ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░ ▒▓▒  ▒▒   ▓▒█░░▓   ▒▒▓  ▒ 
   ░▒ ░ ▒░  ▒   ▒▒ ░ ░▒    ▒   ▒▒ ░ ▒ ░ ░ ▒  ▒ 
   ░░   ░   ░   ▒    ░     ░   ▒    ▒ ░ ░ ░  ░ 
    ░           ░  ░  ░        ░  ░ ░     ░    
                      ░                 ░      
```

[![Python Versions](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Status](https://img.shields.io/badge/status-Beta-yellow)]()

[![asciicast](https://asciinema.org/a/FaO9rQ89jpXwHXx64Cj3ZNCYu.svg)](https://asciinema.org/a/FaO9rQ89jpXwHXx64Cj3ZNCYu)

# RA.Aid

RA.Aid (ReAct Aid) is a powerful AI-driven command-line tool that integrates `aider` (https://aider.chat/) within a LangChain ReAct agent loop. This unique combination allows developers to leverage aider's code editing capabilities while benefiting from LangChain's agent-based task execution framework. The tool provides an intelligent assistant that can help with research, planning, and implementation of development tasks.

⚠️ **IMPORTANT: USE AT YOUR OWN RISK** ⚠️
- This tool **can and will** automatically execute shell commands on your system
- No warranty is provided, either express or implied
- Always review the actions the agent proposes before allowing them to proceed

## Key Features

- **Multi-Step Task Planning**: The agent breaks down complex tasks into discrete, manageable steps and executes them sequentially. This systematic approach ensures thorough implementation and reduces errors.

- **Automated Command Execution**: The agent can run shell commands automatically to accomplish tasks. While this makes it powerful, it also means you should carefully review its actions.

- **Three-Stage Architecture**:
  1. **Research**: Analyzes codebases and gathers context
  2. **Planning**: Breaks down tasks into specific, actionable steps
  3. **Implementation**: Executes each planned step sequentially

What sets RA.Aid apart is its ability to handle complex programming tasks that extend beyond single-shot code edits. By combining research, strategic planning, and implementation into a cohesive workflow, RA.Aid can:

- Break down and execute multi-step programming tasks
- Research and analyze complex codebases to answer architectural questions
- Plan and implement significant code changes across multiple files
- Provide detailed explanations of existing code structure and functionality
- Execute sophisticated refactoring operations with proper planning

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Development Setup](#development-setup)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Three-Stage Architecture**: The workflow consists of three powerful stages:
  1. **Research** 🔍 - Gather and analyze information
  2. **Planning** 📋 - Develop execution strategy
  3. **Implementation** ⚡ - Execute the plan with AI assistance
  
  Each stage is powered by dedicated AI agents and specialized toolsets.
- **Advanced AI Integration**: Built on LangChain and leverages the latest LLMs for natural language understanding and generation.
- **Comprehensive Toolset**:
  - Shell command execution
  - Expert querying system
  - File operations and management
  - Memory management
  - Research and planning tools
  - Code analysis capabilities
- **Interactive CLI Interface**: Simple yet powerful command-line interface for seamless interaction
- **Modular Design**: Structured as a Python package with specialized modules for console output, processing, text utilities, and tools
- **Git Integration**: Built-in support for Git operations and repository management

## Installation

RA.Aid can be installed directly using pip:

```bash
pip install ra-aid
```

### Prerequisites

Before using RA.Aid, you'll need:

1. Python package `aider` installed and available in your PATH:
```bash
pip install aider-chat
```

2. API keys for the required AI services:

```bash
# Required: Set up your Anthropic API key
export ANTHROPIC_API_KEY=your_api_key_here

# Optional: Set up OpenAI API key if using OpenAI features
export OPENAI_API_KEY=your_api_key_here
```

You can get your API keys from:
- Anthropic API key: https://console.anthropic.com/
- OpenAI API key: https://platform.openai.com/api-keys

## Usage

RA.Aid is designed to be simple yet powerful. Here's how to use it:

```bash
# Basic usage
ra-aid -m "Your task or query here"

# Research-only mode (no implementation)
ra-aid -m "Explain the authentication flow" --research-only
```

### Command Line Options

- `-m, --message`: The task or query to be executed (required)
- `--research-only`: Only perform research without implementation

### Example Tasks

1. Code Implementation:
   ```bash
   ra-aid -m "Add input validation to the user registration endpoint"
   ```

2. Code Research:
   ```bash
   ra-aid -m "Explain how the authentication middleware works" --research-only
   ```

3. Refactoring:
   ```bash
   ra-aid -m "Refactor the database connection code to use connection pooling"
   ```

### Environment Variables

RA.Aid uses the following environment variables:

- `ANTHROPIC_API_KEY` (Required): Your Anthropic API key for accessing Claude
- `OPENAI_API_KEY` (Optional): Your OpenAI API key if using OpenAI features

You can set these permanently in your shell's configuration file (e.g., `~/.bashrc` or `~/.zshrc`):

```bash
export ANTHROPIC_API_KEY=your_api_key_here
export OPENAI_API_KEY=your_api_key_here
```

## Architecture

RA.Aid implements a three-stage architecture for handling development and research tasks:

1. **Research Stage**: 
   - Gathers information and context
   - Analyzes requirements
   - Identifies key components and dependencies

2. **Planning Stage**:
   - Develops detailed implementation plans
   - Breaks down tasks into manageable steps
   - Identifies potential challenges and solutions

3. **Implementation Stage**:
   - Executes planned tasks
   - Generates code or documentation
   - Performs necessary system operations

### Core Components

- **Console Module** (`console/`): Handles console output formatting and user interaction
- **Processing Module** (`proc/`): Manages interactive processing and workflow control
- **Text Module** (`text/`): Provides text processing and manipulation utilities
- **Tools Module** (`tools/`): Contains various utility tools for file operations, search, and more

## Dependencies

### Core Dependencies
- `langchain-anthropic`: LangChain integration with Anthropic's Claude
- `langgraph`: Graph-based workflow management
- `rich>=13.0.0`: Terminal formatting and output
- `GitPython==3.1.41`: Git repository management
- `fuzzywuzzy==0.18.0`: Fuzzy string matching
- `python-Levenshtein==0.23.0`: Fast string matching
- `pathspec>=0.11.0`: Path specification utilities

### Development Dependencies
- `pytest>=7.0.0`: Testing framework
- `pytest-timeout>=2.2.0`: Test timeout management

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/ai-christianson/ra-aid.git
cd ra-aid
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Run tests:
```bash
python -m pytest
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

3. Make your changes and commit:
```bash
git commit -m 'Add some feature'
```

4. Push to your fork:
```bash
git push origin feature/your-feature-name
```

5. Open a Pull Request

### Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Keep commits focused and message clear
- Ensure all tests pass before submitting PR

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2024 AI Christianson

## Contact

- **Issues**: Please report bugs and feature requests on our [Issue Tracker](https://github.com/ai-christianson/ra-aid/issues)
- **Repository**: [https://github.com/ai-christianson/ra-aid](https://github.com/ai-christianson/ra-aid)
- **Documentation**: [https://github.com/ai-christianson/ra-aid#readme](https://github.com/ai-christianson/ra-aid#readme)
