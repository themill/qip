CENTOS72 = {
    "server": "dev3d-3",
    "platform": "el7-x86-64",
    "install_dir": "/mill3d/server/apps/PYTHON/QIP/el7-x86-64/packages/",
}

CENTOS65 = {
    "server": "dev3d-2",
    "platform": "el6-x86-64",
    "install_dir": "/mill3d/server/apps/PYTHON/QIP/el6-x86-64/packages/",
}

LOCAL = {
    "server": "localhost",
    "platform": "{{platform}}",
    "install_dir": "/mill3d/server/apps/PYTHON/QIP/{{platform}}/packages/",
}

TARGETS = {
    "centos72": CENTOS72,
    "centos65": CENTOS65,
    "localhost": LOCAL
}
