
INSTALL_DIR = "/mill3d/server/apps/PYTHON/QIP/packages/"
PACKAGE_INDEX = "/mill3d/server/apps/PYTHON/QIP/index/"
DEP_STORE = "/tmp/qip_deps/"

TARGETS = {"centos72": "dev3d-3",
           "centos65": "dev3d-2"}

PIP_CMDS = {"centos72": "/mill3d/server/apps/PYTHON/el7-x86-64/mill_python-2.7.12/bin/pip",
            "centos65": "/mill3d/server/apps/PYTHON/el6-x86-64/mill_python-2.7.12/bin/pip"}