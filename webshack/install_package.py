from .dependencies import identify_dependencies, verify
from collections import deque

class MissingPackageError(KeyError):
    pass

def install_package(package, components_dir):
    package_dir = components_dir / package.name
    deps = set()
    asset_paths = []
    for asset, getter in package.assets.items():
        asset_path = package_dir / asset
        getter(asset_path)
        asset_paths.append(asset_path)
        for dep in identify_dependencies(asset_path):
            deps.add(dep)
    for path in asset_paths:
        verify(path)
    return iter(deps)

def install_package_hierarchy(package, db, components_dir, log_output=lambda x: None):
    worklist = deque((package,))
    while worklist:
        next_item = worklist.popleft()
        log_output(next_item)
        try:
            pkg = db[next_item]
        except KeyError:
            raise MissingPackageError(next_item)
        for new_dep in install_package(db[next_item], components_dir):
            if not (components_dir / new_dep).exists() and new_dep not in worklist:
                worklist.append(new_dep)
        log_output(None)

