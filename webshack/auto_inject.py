from urllib.parse import urljoin
from urllib.request import urlopen
from urllib.error import URLError

import sys

ENORMOUS_INJECTION_HACK = False

GITHUB_USERS = [('Polymer', '0.5.2')]

def resolve_missing_user(user, branch, package):
    assets = ["{}.html".format(package),
              "{}.css".format(package),
              "{}.js".format(package)]
    base_url = "https://raw.githubusercontent.com/{user}/{package}/{branch}/".format(**locals())
    matched_assets = []
    for asset in assets:
        asset_url = urljoin(base_url, asset)
        try:
            with urlopen(asset_url):
                pass
            matched_assets.append(asset)
        except URLError:
            pass
    if matched_assets:
        print("    Matched.")
        data = {'base': base_url, 'assets': {a: a for a in matched_assets}}
        if ENORMOUS_INJECTION_HACK:
            target = open('webshack/standard_packages.yaml', 'a')
        else:
            target = sys.stdout
            print('---')
        print('{}:'.format(package), file=target)
        print('  base: {}'.format(base_url), file=target)
        print('  assets:', file=target)
        for asset in matched_assets:
            print('    {0}: {0}'.format(asset), file=target)
        if not ENORMOUS_INJECTION_HACK:
            print('---')
        return True
    return False

def resolve_missing(package):
    print('Trying to resolve missing package from GitHub repositories...')
    for user, branch in GITHUB_USERS:
        print('  {}...'.format(user))
        if resolve_missing_user(user, branch, package):
            return

