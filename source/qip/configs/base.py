CENTOS72 = {
    "server": "dev3d-3",
    "platform": "el7-x86-64",
    "pipcmd": "/mill3d/server/apps/PYTHON/el7-x86-64/mill_python-2.7.12/bin/pip",
    "install_dir": "/mill3d/server/apps/PYTHON/QIP/el7-x86-64/packages/",
    "package_idx": "/mill3d/server/apps/PYTHON/QIP/el7-x86-64/index/"
}

CENTOS65 = {
    "server": "dev3d-2",
    "platform": "el6-x86-64",
    "pipcmd": "/mill3d/server/apps/PYTHON/el6-x86-64/mill_python-2.7.12/bin/pip",
    "install_dir": "/mill3d/server/apps/PYTHON/QIP/el6-x86-64/packages/",
    "package_idx": "/mill3d/server/apps/PYTHON/QIP/el6-x86-64/index/"
}

LOCAL = {
    "server": "localhost",
    "platform": "{{platform}}",
    "pipcmd": "/mill3d/server/apps/PYTHON/{{platform}}/mill_python-2.7.12/bin/pip",
    "install_dir": "/mill3d/server/apps/PYTHON/QIP/{{platform}}/packages/",
    "package_idx": "/mill3d/server/apps/PYTHON/QIP/{{platform}}/index/"
}

TARGETS = {
    "centos72": CENTOS72,
    "centos65": CENTOS65,
    "localhost": LOCAL
}

LOCATION_LUT = {
    "CHICAGO": "bugsy",
    "LA": "marmont",
    "LONDON": "master",
    "NY": "turing",
    "BANGALORE": "cobra",
}
