from sandbox import *
import sys, pickle, os

def main():
    if not os.path.exists(os.path.join(os.getcwd(), "sandbox_overseer.pickle")):
        overseer = sandbox_overseer()
    else:
        with open('sandbox_overseer.pickle', 'rb') as file:
            # Deserialize and load the object from the file
            overseer = pickle.load(file)
    args = sys.argv
    if len(args) == 2 and args[-1] in ["-h", "--h", "--help", "-help"]:
        print("python-sandbox usage instructions")
        print("1. To start a NEW sandbox BOXNAME:")
        print("python python-sandbox.py start BOX_NAME")
        print("1. To restart a sandbox BOXNAME:")
        print("python python-sandbox.py restart BOX_NAME")
        print("2. To pip install pacakges on sandbox BOXNAME:")
        print("python python-sandbox.py BOX_NAME pip install ARGS")
        print("3. To run a python file on sandbox BOXNAME:")
        print("python python-sandbox.py BOX_NAME python PYFILE.py ARGS...") 
        print("4. To stop a sandbox BOXNAME:")
        print("python python-sandbox.py stop BOX_NAME")
        print("5. To show all sandboxes ")
        print("python python-sandbox.py show-all")
    elif len(args) == 2 and args[-1] == "show-all":
        if overseer.running_sandbox is None and len(overseer.halted_sandboxes) == 0:
            print("There is no sandbox")
        if overseer.running_sandbox is not None:
            print(f"{overseer.running_sandbox}---->RUNNING")
        for stopped_box in overseer.halted_sandboxes:
            print(f"{stopped_box}---->STOPPED")
    elif len(args) == 3 and args[1] == "start":
        box_name = args[-1]
        if len(box_name) < 3:
            print(f"Chosen box name {box_name} is too short")
            return    
        box = sandbox(name=box_name, overseer=overseer)
        overseer.add_box(box)
        assert overseer.boxes[box_name].start()
    elif len(args) == 3 and args[1] == "restart":
        box_name = args[-1]
        assert overseer.restart_sandbox(box_name)
    elif len(args) == 3 and args[1] == "stop":
        box_name = args[-1]  
        assert overseer.boxes[box_name].stop()
    elif len(args) > 3 and args[3].endswith(".py") and args[2] == "python": 
        box_name = args[1]
        py_args = args[3:]
        assert overseer.boxes[box_name].run_py(" ".join(py_args))
    elif len(args) > 4 and args[-3] == "pip" and args[-2] == "install": 
        box_name = args[1]
        pip_args = args[4:]
        assert overseer.boxes[box_name].run_pip_install(" ".join(pip_args))
    else:
        print("Can't understand your instruction, please use --help to get more info")

    with open('sandbox_overseer.pickle', 'wb') as file:
        pickle.dump(overseer, file)

if __name__ == "__main__":
    main()