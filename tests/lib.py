from contextlib import contextmanager
from tempfile import TemporaryDirectory
from pathlib import Path
import subprocess

def replace_ini(contents, key, value):
    def check_line(line):
        if line.startswith(key):
            return '{}={}'.format(key, value)
        return line
    return '\n'.join(check_line(line) for line in contents.splitlines())

def try_mkdir(path):
    try:
        path.mkdir()
    except FileExistsError:
        if not path.is_dir():
            raise

def setup_sdist(repo_path, dest_path):
    sdist_path = dest_path.joinpath('sdist')
    subprocess.run(['python3', 'setup.py', 'sdist', '--dist-dir', sdist_path],
        cwd=repo_path, check=True)
    return sdist_path

def ansible(playbook_path, inventory_path, cwd):
    print(['ansible-playbook', playbook_path,
            '-i', inventory_path])
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
        bookcodes_path = Path(td).joinpath('bookcodes')
        try_mkdir(bookcodes_path)
        inv_path = Path(td).joinpath('ansible_inventory.ini')
        with open(inv_path, 'w') as inv:
            inv.write(inv_contents.format(dist_path=sdist_path,
                bookcodes_path=bookcodes_path))

        data = {'sdist_path': sdist_path, 'vm_addr': '192.168.121.140'}

        try:
            vagrant('up', cwd=repo_path.joinpath('tests')) # may leave an unprovisioned VM
            ansible('ansible/fresh.yml', inv_path, cwd=repo_path)
            ansible('ansible/hosting.yml', inv_path, cwd=repo_path)
            ansible('ansible/users.yml', inv_path, cwd=repo_path)
            ansible('ansible/site2.yml', inv_path, cwd=repo_path)
        except Exception as e:
            if not cleanup:
                import traceback
                traceback.print_exc()
                yield data
            raise e
        else:
            yield data
        finally:
            vagrant('destroy', cwd=repo_path.joinpath('tests'))

