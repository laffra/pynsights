import atexit
from setuptools import setup, find_packages
from setuptools.command.install import install
from subprocess import check_call

REQUIRED_PACKAGES = [
    "websocket-client",
    "psutil",
]


class CustomInstall(install):
    def run(self):
        def _post_install():
            for package in REQUIRED_PACKAGES:
                check_call(['python3', '-m', 'pip', 'install', package])

        atexit.register(_post_install)
        install.run(self)


setup(
    name = 'pyinsights',
    version = '0.1.18',
    packages = find_packages(),
    install_requires = REQUIRED_PACKAGES,
    include_package_data=True,
    cmdclass = {
        'install': CustomInstall,
    },
)