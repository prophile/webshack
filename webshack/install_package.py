from .dependencies import identify_dependencies
from collections import deque

def install_package(package, components_dir):
    package_dir = components_dir / package.name
    deps = set()
    for asset, getter in package.assets.items():
        asset_path = package_dir / asset
        getter(asset_path)
        for dep in identify_dependencies(asset_path):
            deps.add(dep)
    return iter(deps)

def install_package_hierarchy(package, db, components_dir, log_output=lambda x: None):
    worklist = deque((package,))
    while worklist:
        next_item = worklist.popleft()
        log_output(next_item)
        for new_dep in install_package(db[next_item], components_dir):
            if not (components_dir / new_dep).exists() and new_dep not in worklist:
                worklist.append(new_dep)
        log_output(None)

