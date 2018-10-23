from contextlib import contextmanager
from tempfile import TemporaryDirectory
from pathlib import Path
import subprocess


def setup_sdist(repo_path, dest_path):
    subprocess.run(['python3', 'setup.py', 'sdist',
            '--dist-dir', dest_path.joinpath('sdist')],
        cwd=repo_path, check=True)

def ansible(playbook_path, inventory_path, cwd):
    subprocess.run(['ansible-playbook', playbook_path,
            '-i', inventory_path],
        cwd=cwd,
        check=True)

def vagrant(command, cwd):
    subprocess.run(['vagrant', command], cwd=cwd, check=True)
 
@contextmanager
def vm(repo_path, cleanup=True):
    with open(repo_path.joinpath('tests/ansible_inventory.ini')) as inv:
        inv_contents = inv.read()

    with TemporaryDirectory() as td:
        setup_sdist(repo_path, dest_path=Path(td))
        sdist_path = Path(td).joinpath('sdist')
        inv_path = Path(td).joinpath('ansible_inventory.ini')
        with open(inv_path, 'w') as inv:
            inv.write(inv_contents.format(dist_path=sdist_path))

        try:
            vagrant('up', cwd=repo_path.joinpath('tests')) # may leave an unprovisioned VM
            ansible('ansible/fresh.yml', inv_path, cwd=repo_path)
            ansible('ansible/hosting.yml', inv_path, cwd=repo_path)
            ansible('ansible/site2.yml', inv_path, cwd=repo_path)
            yield
        finally:
            if cleanup:
                vagrant('destroy', cwd=repo_path.joinpath('tests'))

