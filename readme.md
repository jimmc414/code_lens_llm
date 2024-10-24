# CodeLensLLM Documentation

## Overview

CodeLensLLM is a tool designed to analyze Python codebases and extract function and class signatures using Abstract Syntax Trees (AST). This tool is of value for developers working with Large Language Models (LLMs) who need to efficiently analyze and describe large Python codebases while maximizing limited context windows.  This program would facilitate a pre-read of a codebase for an LLM.  Tokens used for this summarization are about 10% of the size of the code base if it were passed in as text. 

### Key Features
- Extracts function and method signatures using AST parsing
- Optional inclusion of docstrings
- Support for async functions and methods
- Type annotation preservation
- Hierarchical output structure (files → classes → methods)
- Configurable empty item reporting
- JSON output for easy integration

### Target Audience
- Developers working with LLMs who need concise codebase representations
- Users analyzing large Python codebases
- Developers performing code analysis and documentation tasks

## Installation

### Prerequisites
- Python 3.8 or higher
- Required libraries:
  - `argparse` (standard library)
  - `ast` (standard library)
  - `json` (standard library)
  - `logging` (standard library)

### Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/your-repo/code_lens_llm.git
cd code_lens_llm
```

2. (Optional) Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies (if any additional are added in the future):
```bash
pip install argparse ast json logging typing
```

## Usage

### Basic Usage

Extract signatures from a codebase:
```bash
python code_lens_llm.py /path/to/codebase
```

### Advanced Options

1. Specify custom output file:
```bash
python code_lens_llm.py /path/to/codebase -o custom_output.json
```

2. Configure via Global Settings:
```python
# At the top of the script:
OMIT_DOCSTRINGS = True  # Exclude docstrings from output
REPORT_EMPTY_ITEMS = False  # Include empty items in output
```

### Output Format

The tool generates a JSON file with the following structure:
```json
{
    "relative/path/to/file.py": {
        "functions": {
            "function_name": {
                "signature": "(param1: str, param2: int = 0) -> bool",
                "docstring": "Function documentation..."
            }
        },
        "classes": {
            "ClassName": {
                "docstring": "Class documentation...",
                "methods": {
                    "method_name": {
                        "signature": "(self, param1: str) -> None",
                        "docstring": "Method documentation..."
                    }
                }
            }
        }
    }
}
```

## API Reference

### Core Functions

#### `setup_logging()`
Configures the logging mechanism for the script.
- **Returns**: None
- **Configuration**: Sets INFO level with format '%(levelname)s: %(message)s'

#### `get_python_files(codebase_path: str) -> List[str]`
Recursively collects Python files from the given directory.
- **Parameters**:
  - `codebase_path`: Directory path to search for Python files
- **Returns**: List of absolute paths to Python files
- **Raises**: None (logs errors if encountered)

#### `extract_signatures_with_ast(file_path: str, include_docstrings: bool = False) -> Dict[str, Any]`
Extracts signatures from a single Python file using AST.
- **Parameters**:
  - `file_path`: Path to Python file
  - `include_docstrings`: Whether to include docstrings in output
- **Returns**: Dictionary containing functions and classes with their signatures
- **Raises**: Logs SyntaxError or other exceptions if encountered

#### `get_function_signature(func_node: ast.FunctionDef, is_async: bool = False) -> str`
Constructs a function signature string from an AST node.
- **Parameters**:
  - `func_node`: AST node representing a function
  - `is_async`: Whether the function is async
- **Returns**: String representation of the function signature
- **Special handling**: Includes type annotations and default values when available

#### `extract_signatures_with_ast_method(codebase_path: str, python_files: List[str], include_docstrings: bool = False) -> Dict[str, Any]`
Processes multiple Python files and combines their signatures.
- **Parameters**:
  - `codebase_path`: Base directory path
  - `python_files`: List of Python file paths
  - `include_docstrings`: Whether to include docstrings
- **Returns**: Dictionary mapping file paths to their signature information

### Global Configuration

- `OMIT_DOCSTRINGS`: Controls docstring inclusion (default: False)
- `REPORT_EMPTY_ITEMS`: Controls empty item reporting (default: True)

## Troubleshooting

### Common Issues and Solutions

1. **Invalid Directory Path**
   - Error: "The path {path} is not a valid directory."
   - Solution: Ensure the provided path exists and is accessible

2. **No Python Files Found**
   - Error: "No Python files found in {path}."
   - Solution: Verify that the directory contains .py files

3. **Syntax Errors in Python Files**
   - Error: "Syntax error in {file_path}: {error}"
   - Solution: Fix the syntax error in the indicated file

4. **Output File Writing Failures**
   - Error: "Failed to write output to {output_path}: {error}"
   - Solution: Ensure write permissions and valid path

## Glossary

- **AST (Abstract Syntax Tree)**: A tree representation of Python code's syntactic structure, used for analyzing code without executing it.
- **Docstring**: A string literal that appears as the first statement in a module, function, class, or method, used for documentation.
- **Signature**: The function or method declaration, including its name, parameters, type hints, and return type.
- **Context Window**: The maximum amount of text that can be processed by an LLM in a single interaction.