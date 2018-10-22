#!/usr/bin/python3
from pathlib import Path
import subprocess
from contextlib import contextmanager
from enum import IntEnum
from tempfile import TemporaryDirectory
from collections import namedtuple

REPO_PATH = Path(__file__).absolute().parent.parent


class TestError(Exception): pass

def assert_file(path):
    if not path.is_file():
        raise TestError("{} is not a file".format(path))


def ansible(playbook_path, inventory_path, cwd):
    subprocess.run(['ansible-playbook', playbook_path,
            '-i', inventory_path],
        cwd=cwd,
        check=True)

def vagrant(command, cwd):
    subprocess.run(['vagrant', command], cwd=cwd, check=True)

def setup_sdist(script_dir, dest_path):
    subprocess.run(['python3', script_dir.joinpath('setup.py'), 'sdist',
            '--dist-dir', dest_path.joinpath('sdist')],
        cwd=script_dir, check=True)

def test_install(ctx):
    setup_sdist(ctx.repo_path, dest_path=ctx.tempdir)
    with open(ctx.repo_path.joinpath('tests/ansible_inventory.ini')) as inv:
        inv_contents = inv.read()
    inv_path = ctx.tempdir.joinpath('ansible_inventory.ini')
    with open(inv_path, 'w') as inv:
        inv.write(inv_contents.format(dist_path=ctx.tempdir.joinpath('sdist')))

    try:
        vagrant('up', cwd=ctx.repo_path.joinpath('tests')) # may leave an unprovisioned VM
        ansible('ansible/fresh.yml', inv_path, cwd=ctx.repo_path)
        ansible('ansible/hosting.yml', inv_path, cwd=ctx.repo_path)
        ansible('ansible/site2.yml', inv_path, cwd=ctx.repo_path)
    finally:
        vagrant('destroy', cwd=ctx.repo_path.joinpath('tests'))

def test_sdist(ctx):
    setup_sdist(ctx.repo_path, dest_path=ctx.tempdir)
    assert_file(ctx.tempdir.joinpath('sdist/Marginalia-0.1.tar.gz'))

class TestContext(namedtuple('TestContext', ['tempdir', 'repo_path'])): pass

@contextmanager
def get_test_context(repo_path):
    with TemporaryDirectory() as d:
        yield TestContext(Path(d), repo_path)

if __name__ == '__main__':
    for test in [test_sdist, test_install]:
        with get_test_context(REPO_PATH) as ctx:
            test(ctx)
