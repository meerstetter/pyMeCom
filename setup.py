from setuptools import setup

setup(
    name='mecom',
    version='1.1',
    packages=['mecom'],
    install_requires = ['pySerial>=3.4'],
    url='https://github.com/meerstetter/pyMeCom',
    license='MIT',
    author='Suthep Pomjaksilp',
    author_email='pomjaksi@physik.uni-kl.de', # Please contact Meerstetter Engineering for support
    description='Python interface for Meerstetter TEC controller devices'
)
