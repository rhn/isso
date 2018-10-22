#!/usr/bin/python3
from pathlib import Path
import subprocess
from contextlib import contextmanager
from enum import IntEnum

REPO_PATH = Path(__file__).parent.parent

def run_ansible(repo_path, playbook_name):
    subprocess.run(['ansible-playbook',
            '-i', repo_path.joinpath('tests/ansible_inventory.ini'),
            repo_path.joinpath(playbook_name)],
        check=True)

def run_vagrant(repo_path, command):
    subprocess.run(['vagrant', command], cwd=repo_path.joinpath('tests'), check=True)

class VMStage(IntEnum):
    user = 1
    nginx = 2
    marginalia = 3

    @classmethod
    def from_string(cls, s):
        for name, member in cls.__members__.items():
            if s == name:
                return member
        raise ValueError("No element {} in {}".format(s, cls))

@contextmanager
def vm(repo_path, install_stage, cleanup=True):
    try:
        run_vagrant(repo_path, 'up') # may leave an unprovisioned VM
        run_ansible(repo_path, 'ansible/fresh.yml')
        if install_stage > VMStage.user:
            run_ansible(repo_path, 'ansible/hosting.yml')
            if install_stage > VMStage.nginx:
                run_ansible(repo_path, 'ansible/site2.yml')
        yield
    finally:
        if cleanup:
            run_vagrant(repo_path, 'destroy')

def test_install(repo_path):
    with vm(repo_path, VMStage.marginalia):
        pass

if __name__ == '__main__':
    test_install(REPO_PATH)
