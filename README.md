# pyMeCom
A python interface for the MeCom protocol by Meerstetter.
This package was developed to control several TEC devices on a raspberry pi by connecting them via usb or via tcp.

## Requirements
1. this code is only tested in Python 3 running in a linux OS
1. `pySerial` in a version `>= 3.1` https://pypi.python.org/pypi/pyserial

## Installation
1. clone the repository
1. setup a virtualenv in python (you may skip this step)
1. install the package with either pip or setuptools, e.g. `pip install --user .`
1. `python mecom/mecom.py` to see some example output

## Usage
For a basic example look at `mecom/mecom.py`, the `__main__` part contains an example communication.

## Additional parameters to get/set
Only parameters present in `mecom/commands.py` can be used with the regular functions, this is a security feature in case someone uses a parameter like "flash firmware" by accident.
Use the *_raw functions if you need access to parameters not in `mecom/commands.py`.
Furthermore, feel free to add more parameters to `mecom/commands.py`.

## Contribution
This is by no means a polished software, contribution by submitting to this repository is appreciated.

## Citation
Cite as `Pomjaksilp, Suthep et al. (2024). pyMeCom 1.0. Zenodo. 10.5281/zenodo.11233757`