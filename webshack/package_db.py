from collections import namedtuple
import collections.abc
from urllib.parse import urljoin, quote, urlsplit
from urllib.request import urlretrieve
import yaml
from pkg_resources import resource_string

class PackageDatabase(collections.abc.Mapping):
    def __init__(self):
        self._packages = {}

    def add(self, package):
        self._packages[package.name] = package

    def __getitem__(self, item):
        return self._packages[item]

    def __iter__(self):
        return iter(self._packages)

    def __len__(self):
        return len(self._packages)

Package = namedtuple('Package', 'name assets')

def _create_parents(path):
    try:
        path.parent.mkdir(parents=True)
    except FileExistsError:
        pass

def uri_asset(uri, base='.'):
    full_uri = urljoin(base, uri)
    def download(path):
        _create_parents(path)
        urlretrieve(full_uri, str(path))
    return download

def script_pseudo_asset(script, dependencies):
    def generate(path):
        _create_parents(path)
        with path.open('w') as f:
            f.write('<script src="{}"></script>\n\n'.format(quote(script)))
            for dep in dependencies:
                f.write('<link rel="import" href="{}">\n'.format(quote(dep)))
    return generate

def create_package(name, settings):
    assets = {}
    package_type = settings.get('type', 'standard')
    base = settings.get('base', '.')
    if package_type == 'standard':
        for asset, source in settings['assets'].items():
            assets[asset] = uri_asset(source, base)
    elif package_type == 'library':
        source = settings['src']
        components = urlsplit(source)
        filename = components.path.split('/')[-1]
        assets[filename] = uri_asset(source)
        dependencies = settings.get('dependencies', ())
        assets['{}.html'.format(name)] = script_pseudo_asset(filename, ['../{0}/{0}.html'.format(package) for package in dependencies])
    return Package(name=name, assets=assets)

def load_package_db(data, db):
    data = yaml.load(data)
    for package, settings in data.items():
        db.add(create_package(package, settings))

def standard_package_db():
    db = PackageDatabase()
    data = resource_string(__name__, 'standard_packages.yaml')
    load_package_db(data, db)
    return db

