from setuptools import setup, find_packages

# Default version information
path = 'mecom'
__version__ = '0.1'
install_requirements = ['pySerial>=3.4',
                        'PyCRC',
                        'pandas>=0.20.0']
packages = [package for package in find_packages(path)]


# Define your setup
# version should be considered using git's short or better the full hash
def get_version_from_git():
    """
    Get the short version string of a git repository
    :return: (str) version information
    """
    import subprocess
    try:
        v = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
        return __version__ + v
    except Exception as ex:
        print("Could not retrieve git version information")
        print("#" * 30)
        print(ex)
    return __version__  # default


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='pymecom',
      version=__version__,
      description="pyMeCom version={version}".format(version=str(get_version_from_git())),
      url='http://bec-git.physik.uni-kl.de/suthep/pymecom',
      author='Suthep Pomjaksilp',
      author_email='sp@laz0r.de',
      packages=packages,
      package_dir={'': path},
      install_requires=install_requirements
      )
