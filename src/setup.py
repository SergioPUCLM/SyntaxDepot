"""
Path setup module.
This module sets up the paths for the imports in the project.
Allows importing modules from 'src/', 'data/', and 'res/' directories.

Example: from src.module_name import function_name
"""

import os
import sys


def setup_paths():
    """
    Set up the paths for the imports.
    """
    # Get the absolute path of the project's root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(os.path.join(project_root, "src"))  # Add 'src/'
    sys.path.append(os.path.join(project_root, "data"))  # Add 'data/'
    sys.path.append(os.path.join(project_root, "res"))  # Add 'res/'
    