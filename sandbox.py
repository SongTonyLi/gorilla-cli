import os
import subprocess

class sandbox_overseer:
    def __init__(self, lima_bin_loc=None):
        # currently only one sandbox is allowed at a time
        self.boxes = dict()
        self.running_sandbox = None
        self.halted_sandboxes = set()
        lima_bin_path = os.path.join(os.getcwd(), "lima", "bin") 
        self.limactl = os.path.join(lima_bin_path, "limactl") if lima_bin_loc is None else os.path.join(lima_bin_loc, "limactl")
    
    def add_box(self, box):
        self.boxes[box.name] = box

    def run_command(self, command: str):
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"Error executing command: {command}")
            return False
        else:
            return True
        
    def process_command_request(self, sandbox_name: str, command: str):
        # Currently only running sandbox's command would be processed
        # More policies should be updated
        if sandbox_name != self.running_sandbox:
            print("Invalid sandbox")
            return False
        else:
            self.run_command(command)
            return True
    
    def process_vm_script_request(self, sandbox_name: str, shell_script: str):
        if sandbox_name != self.running_sandbox:
            print("Invalid sandbox")
            return False
        result = subprocess.run(f"{self.limactl} shell {sandbox_name} {shell_script}", shell=True) 
        if result.returncode != 0:
            print(f"Error executing command: {shell_script}")
            return False
        else:
            return True

    def create_sandbox(self, sandbox_name: str):   
        if sandbox_name in self.halted_sandboxes or sandbox_name == self.running_sandbox:
            print("Sandbox name already used")
            return False 
        # Default home directory ~/.lima
        home_dir = os.path.expanduser("~")
        sandbox_path = os.path.join(home_dir, ".lima", sandbox_name)
        if not os.path.exists(sandbox_path):
            self.run_command(f"{self.limactl} create python-sandbox.yml --name={sandbox_name}")
            print(f"{sandbox_name} created successfully!")
            return True
        else:
            print(f"{sandbox_name} had already instantiated")
            return True
    
    def start_sandbox(self, sandbox_name: str):
        if not self.create_sandbox(sandbox_name):
            return False
        print(f"Starting sandbox {sandbox_name}!")
        if sandbox_name == self.running_sandbox:
            print(f"Sandbox {sandbox_name} already started")
            return True
        if not self.run_command(f"{self.limactl} start {sandbox_name}"):
            print(f"Sandbox {sandbox_name} failed to start")
            return False
        print(f"Sandbox {sandbox_name} started successfully!")
        self.running_sandbox = sandbox_name
        return True

    def restart_sandbox(self, sandbox_name: str):
        if not self.running_sandbox is None:
            print(f"Sandbox {self.running_sandbox} is running, can't restart {sandbox_name}")
            return False
        if not sandbox_name in self.halted_sandboxes:
            print(f"Sandbox {sandbox_name} doesn't exist in stopped list")
            return False 
        print(f"Restarting sandbox {sandbox_name}")
        if not self.run_command(f"{self.limactl} start {sandbox_name}"):
            print(f"Sandbox {sandbox_name} failed to restart")
            return False
        print(f"Sandbox {sandbox_name} restarted successfully!")
        self.running_sandbox = sandbox_name
        self.halted_sandboxes.remove(sandbox_name)
        return True

    def stop_sandbox(self, sandbox_name: str):
        if sandbox_name != self.running_sandbox:
            print("Invalid sandbox")
            return False
        print(f"Stoping sandbox {sandbox_name}!")
        if sandbox_name in self.halted_sandboxes:
            print(f"Sandbox {sandbox_name} already stopped")
            return True
        if not self.run_command(f"{self.limactl} stop {sandbox_name}"):
            print(f"Sandbox {sandbox_name} can't be stopped")
            return False
        print(f"Sandbox {sandbox_name} stoped successfully!")
        self.running_sandbox = None
        self.halted_sandboxes.add(sandbox_name)
        return True

class sandbox:
    def __init__(self, name: str, overseer: sandbox_overseer):
        self.name = name
        self.venv_name = self.name + "_venv"
        self.venv_created = False
        self.overseer = overseer

    def command_request(self, command: str):
        # sandbox's command request to overseer should be approved
        return self.overseer.process_command_request(self.name, command)
    
    def vm_script_request(self, script: str):
        # sandbox's vm script request to overseer should be approved
        return self.overseer.process_vm_script_request(self.name, script)
    
    def start(self):
        if not self.overseer.start_sandbox(self.name):
            return False
        # every python sandbox should have a virtual environment
        if not self.venv_created:
            if not self.setup_venv():
                print(f"Sandbox {self.name} can't create a virtual env.")
                return False
            else:
                self.venv_created = True
        return True

    def stop(self):
        return self.overseer.stop_sandbox(self.name)
    
    def run_py(self, py_script):
        # check if venv installed
        if not self.venv_created:
            print("Virtual environment has not created")
            return False
        print(f"Executing Python script {py_script} in VM")
        return self.vm_script_request(f"{self.venv_name}/bin/python3 {py_script}")

    def run_pip_install(self, pip_script):
        # check if venv installed
        if not self.venv_created:
            print("Virtual environment has not created")
            return False
        return self.vm_script_request(f"{self.venv_name}/bin/pip3 install {pip_script}")

    def setup_venv(self):
        if not self.vm_script_request(f"mkdir -p {self.venv_name}"): return False
        if not self.vm_script_request("sudo apt-get upgrade"): return False
        if not self.vm_script_request("sudo apt-get install python3-venv"): return False
        if not self.vm_script_request(f"python3 -m venv {self.venv_name}"): return False
        if not self.vm_script_request(f"source {self.venv_name}/bin/activate"): return False
        return True