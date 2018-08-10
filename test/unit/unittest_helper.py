# :coding: utf-8


# Fake logger to remove mlog dependency for tests
class Logger(object):
    def debug(self, msg, **kwargs):
        print msg

    def warning(self, msg, **kwargs):
        print msg

    def error(self, msg, **kwargs):
        print msg

    def info(self, msg, **kwargs):
        print msg


# The test target is localhost with /tmp target folders
TEST = {
    "server": "localhost",
    "platform": "el7-x86-64",
    "pipcmd":
        "/mill3d/server/apps/PYTHON/el7-x86-64/mill_python-2.7.12/bin/pip",
    "install_dir": "/tmp/test-packages/",
    "package_idx": "/tmp/test-index/"
}
