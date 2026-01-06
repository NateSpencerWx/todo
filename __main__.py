#!/usr/bin/env python3
"""Allow running the todo directory as a package: python todo_directory or python ."""
import runpy
import sys
import os

# Get the directory of this __main__.py file
package_dir = os.path.dirname(os.path.abspath(__file__))

# Run the todo.py script in this directory
todo_script = os.path.join(package_dir, 'todo.py')
if not os.path.exists(todo_script):
    print(f"Error: Could not find todo.py at {todo_script}", file=sys.stderr)
    sys.exit(1)

runpy.run_path(todo_script, run_name='__main__')