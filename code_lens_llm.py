import os
import sys
import argparse
import ast
import json
import logging
from typing import List, Dict, Any

# Configuration:
OMIT_DOCSTRINGS = False  # Set to True to omit docstrings, False to include them
REPORT_EMPTY_ITEMS = True  # Set to True to remove empty items, False to keep them

def setup_logging():
    """
    Configure logging for the script.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

def get_python_files(codebase_path: str) -> List[str]:
    """
    Recursively collect all Python (.py) files in the given codebase path.
    """
    python_files = []
    for root, _, files in os.walk(codebase_path):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                python_files.append(full_path)
    logging.info(f"Found {len(python_files)} Python files.")
    return python_files

def extract_signatures_with_ast(file_path: str, include_docstrings: bool = False) -> Dict[str, Any]:
    """
    Parse a Python file using AST to extract function and method signatures.
    Optionally include docstrings based on the include_docstrings flag.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            node = ast.parse(file.read(), filename=file_path)
    except SyntaxError as e:
        logging.error(f"Syntax error in {file_path}: {e}")
        return {}
    except Exception as e:
        logging.error(f"Failed to parse {file_path}: {e}")
        return {}

    module_info = {'functions': {}, 'classes': {}}

    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            signature = get_function_signature(item)
            func_info = {'signature': signature}
            if include_docstrings:
                docstring = ast.get_docstring(item)
                func_info['docstring'] = docstring if docstring else ""
            module_info['functions'][item.name] = func_info
        elif isinstance(item, ast.AsyncFunctionDef):
            signature = get_function_signature(item, is_async=True)
            func_info = {'signature': signature}
            if include_docstrings:
                docstring = ast.get_docstring(item)
                func_info['docstring'] = docstring if docstring else ""
            module_info['functions'][item.name] = func_info
        elif isinstance(item, ast.ClassDef):
            class_info = {}
            class_docstring = ast.get_docstring(item) if include_docstrings else None
            for class_item in item.body:
                if isinstance(class_item, ast.FunctionDef):
                    signature = get_function_signature(class_item)
                    method_info = {'signature': signature}
                    if include_docstrings:
                        method_docstring = ast.get_docstring(class_item)
                        method_info['docstring'] = method_docstring if method_docstring else ""
                    class_info[class_item.name] = method_info
                elif isinstance(class_item, ast.AsyncFunctionDef):
                    signature = get_function_signature(class_item, is_async=True)
                    method_info = {'signature': signature}
                    if include_docstrings:
                        method_docstring = ast.get_docstring(class_item)
                        method_info['docstring'] = method_docstring if method_docstring else ""
                    class_info[class_item.name] = method_info
            class_entry = {'methods': class_info}
            if include_docstrings:
                class_entry['docstring'] = class_docstring if class_docstring else ""
            module_info['classes'][item.name] = class_entry

    if REPORT_EMPTY_ITEMS:
        # Remove empty 'functions' and 'classes' dictionaries
        if not module_info['functions']:
            del module_info['functions']
        if not module_info['classes']:
            del module_info['classes']
        
        # Remove empty 'docstring's from functions
        for func_name, func_info in list(module_info.get('functions', {}).items()):
            if 'docstring' in func_info and not func_info['docstring']:
                del func_info['docstring']
            # If the function dict becomes empty after removing 'docstring', delete the function
            if not func_info:
                del module_info['functions'][func_name]
        
        # Remove empty 'docstring's from classes and their methods
        for class_name, class_details in list(module_info.get('classes', {}).items()):
            # Remove 'docstring' if empty
            if 'docstring' in class_details and not class_details['docstring']:
                del class_details['docstring']
            
            # Remove empty 'docstring's from methods
            for method_name, method_info in list(class_details.get('methods', {}).items()):
                if 'docstring' in method_info and not method_info['docstring']:
                    del method_info['docstring']
                # If the method dict becomes empty after removing 'docstring', delete the method
                if not method_info:
                    del class_details['methods'][method_name]
            
            # Remove 'methods' if empty after cleaning
            if 'methods' in class_details and not class_details['methods']:
                del class_details['methods']
            
            # If the class dict becomes empty after removing 'docstring' and 'methods', delete the class
            if not class_details:
                del module_info['classes'][class_name]

    return module_info

def get_function_signature(func_node: ast.FunctionDef, is_async: bool = False) -> str:
    """
    Construct a function signature string from an AST FunctionDef node.
    """
    args = []
    defaults = {len(func_node.args.args) - len(func_node.args.defaults) + i: default
                for i, default in enumerate(func_node.args.defaults)}
    for i, arg in enumerate(func_node.args.args):
        arg_str = arg.arg
        # Handle default values
        if i in defaults:
            try:
                default_value = ast.unparse(defaults[i]) if hasattr(ast, 'unparse') else '...'
            except:
                default_value = '...'
            arg_str += f"={default_value}"
        # Handle type annotations
        if arg.annotation:
            try:
                annotation = ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else '...'
            except:
                annotation = '...'
            arg_str += f": {annotation}"
        args.append(arg_str)
    # Handle *args and **kwargs
    if func_node.args.vararg:
        vararg = func_node.args.vararg.arg
        if func_node.args.vararg.annotation:
            try:
                annotation = ast.unparse(func_node.args.vararg.annotation) if hasattr(ast, 'unparse') else '...'
            except:
                annotation = '...'
            vararg += f": {annotation}"
        args.append(f"*{vararg}")
    if func_node.args.kwarg:
        kwarg = func_node.args.kwarg.arg
        if func_node.args.kwarg.annotation:
            try:
                annotation = ast.unparse(func_node.args.kwarg.annotation) if hasattr(ast, 'unparse') else '...'
            except:
                annotation = '...'
            kwarg += f": {annotation}"
        args.append(f"**{kwarg}")
    signature = f"({', '.join(args)})"
    if func_node.returns:
        try:
            return_annotation = ast.unparse(func_node.returns) if hasattr(ast, 'unparse') else '...'
        except:
            return_annotation = '...'
        signature += f" -> {return_annotation}"
    if is_async:
        signature = "async " + signature
    return signature

def extract_signatures_with_ast_method(codebase_path: str, python_files: List[str], include_docstrings: bool = False) -> Dict[str, Any]:
    """
    Extract signatures from all Python files using AST.
    Optionally include docstrings based on the include_docstrings flag.
    """
    result = {}
    for file_path in python_files:
        signatures = extract_signatures_with_ast(file_path, include_docstrings=include_docstrings)
        if signatures or not REPORT_EMPTY_ITEMS:
            relative_path = os.path.relpath(file_path, codebase_path)
            result[relative_path] = signatures
    return result

def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Extract function and class signatures from a Python codebase using AST."
    )
    parser.add_argument(
        'codebase_path',
        type=str,
        help='Path to the Python codebase.'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='ast_signature_output.json',
        help='Output file name (default: ast_signature_output.json).'
    )
    args = parser.parse_args()

    codebase_path = args.codebase_path

    if not os.path.isdir(codebase_path):
        logging.error(f"The path {codebase_path} is not a valid directory.")
        sys.exit(1)

    python_files = get_python_files(codebase_path)
    if not python_files:
        logging.error(f"No Python files found in {codebase_path}.")
        sys.exit(1)

    logging.info("Extracting signatures with AST...")
    all_signatures = extract_signatures_with_ast_method(
        codebase_path,
        python_files,
        include_docstrings=not OMIT_DOCSTRINGS  # Include docstrings if OMIT_DOCSTRINGS is False
    )

    output_path = args.output
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_signatures, f, indent=4)
        logging.info(f"AST signature output written to {output_path}")
    except Exception as e:
        logging.error(f"Failed to write output to {output_path}: {e}")
        sys.exit(1)

    logging.info("Extraction complete.")

if __name__ == "__main__":
    main()
