import atexit
from distutils import cmd
from setuptools import setup, find_packages
from setuptools.command.install import install
from subprocess import check_call

REQUIRED_PACKAGES = [
    'websockets',
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
    version = '0.1.4',
    packages = find_packages(),
    install_requires = REQUIRED_PACKAGES,
    include_package_data=True,
    cmdclass = {
        'install': CustomInstall,
    },
)