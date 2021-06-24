from setuptools import setup

setup(
    name='mecom',
    version='0.1',
    packages=['mecom'],
    install_requires = ['pySerial>=3.4',
                        'pythoncrc'],
    url='https://github.com/spomjaksilp/pyMeCom',
    license='',
    author='Suthep Pomjaksilp',
    author_email='pomjaksi@physik.uni-kl.de',
    description='Python interface for Meerstetter TEC controller devices'
)