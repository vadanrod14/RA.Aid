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

# RA.Aid

RA.Aid (ReAct Aid) is a powerful AI-driven command-line tool that integrates `aider` (https://aider.chat/) within a LangChain ReAct agent loop. This unique combination allows developers to leverage aider's code editing capabilities while benefiting from LangChain's agent-based task execution framework. The tool provides an intelligent assistant that can help with research, planning, and implementation of development tasks.

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

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Steps

1. Install from PyPI:
```bash
pip install ra-aid
```

Or install from source:
```bash
git clone https://github.com/ai-christianson/ra-aid.git
cd ra-aid
pip install .
```

2. Install additional dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

## Usage

RA.Aid is used via the `ra-aid` command. The basic usage pattern is:

```bash
ra-aid [task]
```

### Examples

Research a topic:
```bash
ra-aid "Research best practices for Python package structure"
```

Plan a development task:
```bash
ra-aid "Plan the implementation of a new REST API endpoint"
```

Generate code or documentation:
```bash
ra-aid "Create a README.md template for my project"
```

### Interactive Mode

For an interactive session where you can enter multiple tasks:

```bash
ra-aid
```

This will start an interactive prompt where you can input tasks sequentially.

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
