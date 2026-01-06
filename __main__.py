#!/usr/bin/env python3
"""Allow running the todo package as a module: python -m todo or python todo_directory"""
import runpy
import sys
import os

# Get the directory of this __main__.py file
package_dir = os.path.dirname(os.path.abspath(__file__))

# Run the todo.py script in this directory
todo_script = os.path.join(package_dir, 'todo.py')
runpy.run_path(todo_script, run_name='__main__')
