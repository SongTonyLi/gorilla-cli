# Python Sandbox in Linux 

Python Sandbox allows you to run your python codes in a complete linux virtual machine. It is easy to use and efficient. The VM is customizable and you can choose your own CPU, disk size, and RAM size. 

Two key features:
 - Automatic python virtual environment setup.
 - Same python instructions

## Numpy Example listed in samples/1st.gif
![](samples/1st.gif)

## Gorilla CLI Example listed in samples/gorillaVM.gif
![](samples/gorillaVM.gif)

## Requirements
Please install `qemu` on your machine. Currently, python-sandbox only works on MacOS with M-sereis chips. Windows and Linux versions are not yet tested, and they may potentially work.

## Usage

Darg all relevant python files into this folder. Then, type to see instructions you need to do:
```bash
$ python python-sandbox.py --help
```

## How It Works

python-sandbox internally use lima to create a linux virtual machine. You can edit your linux machine profile in `python-sandbox.yml`. It regulates all of sandboxes you created and make sure there is no conflicts between sandboxes.

### Arguments
To start a sandbox
```bash
python python-sandbox.py start NEWBOX
```
To stop a sandbox
```bash
python python-sandbox.py stop NEWBOX
```
#### Warning: always remember to stop a sandbox! The sanbox does not close on itself. 

To run python 
```bash
python python-sandbox.py python PYFILE.py ARGS
```
To pip install relevant packages
```bash
python python-sandbox.py pip install ARGS
```
To show every sandbox status
```bash
python python-sandbox.py show-all
```

