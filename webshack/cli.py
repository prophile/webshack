"""WebShack: Sensible web components.

Usage:
  webshack list
  webshack get <package>...
  webshack -h | --help
  webshack --version

Options:
  -h --help         Show this screen.
  --version         Show version.
"""

import sys
from docopt import docopt

from termcolor import colored

from webshack.install_package import install_package_hierarchy
import webshack.package_db as pdb
from pathlib import Path

VERSION="0.0.1"

class CLIOutput:
    def __init__(self):
        self.shift_width = 0

    def log(self, package):
        if package is None:
            self.end_package()
        else:
            self.begin_package(package)

    def begin_package(self, package):
        self.shift_width = 50 - len(package)
        sys.stdout.write("Installing {pkg}...".format(pkg=colored(package, 'blue')))
        sys.stdout.flush()

    def end_package(self):
        sys.stdout.write(' '*self.shift_width)
        sys.stdout.write('[{}]\n'.format(colored('DONE', 'green', attrs=['bold'])))
        sys.stdout.flush()

def main():
    options = docopt(__doc__, version=VERSION)
    db = pdb.standard_package_db()
    components = Path('components')
    if options['get']:
        output = CLIOutput()
        for package in options['<package>']:
            install_package_hierarchy(package, db, components,
                                      log_output=output.log)
    elif options['list']:
        for package in sorted(db):
            print(package)

