"""WebShack: Sensible web components.

Usage:
  webshack get <package>...
  webshack -h | --help
  webshack --version

Options:
  -h --help         Show this screen.
  --version         Show version.
"""

import sys
from docopt import docopt

from webshack.install_package import install_package_hierarchy
import webshack.package_db as pdb
from pathlib import Path

VERSION="0.0.1"

def main():
    options = docopt(__doc__, version=VERSION)
    db = pdb.standard_package_db()
    components = Path('components')
    if options['get']:
        for package in options['<package>']:
            install_package_hierarchy(package, db, components)

