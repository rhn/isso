from contextlib import contextmanager
from tempfile import TemporaryDirectory
from pathlib import Path

import test


@contextmanager
def vm(repo_path, cleanup=True):
    with open(repo_path.joinpath('tests/ansible_inventory.ini')) as inv:
        inv_contents = inv.read()

    with TemporaryDirectory() as td:
        test.setup_sdist(repo_path, dest_path=Path(td))
        sdist_path = Path(td).joinpath('sdist')
        inv_path = Path(td).joinpath('ansible_inventory.ini')
        with open(inv_path, 'w') as inv:
            inv.write(inv_contents.format(dist_path=sdist_path))

        try:
            test.vagrant('up', cwd=repo_path.joinpath('tests')) # may leave an unprovisioned VM
            test.ansible('ansible/fresh.yml', inv_path, cwd=repo_path)
            test.ansible('ansible/hosting.yml', inv_path, cwd=repo_path)
            test.ansible('ansible/site2.yml', inv_path, cwd=repo_path)
            yield
        finally:
            if cleanup:
                test.vagrant('destroy', cwd=repo_path.joinpath('tests'))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--keep', action='store_true', help='Keep the VM if creation fails')
    args = parser.parse_args()

    try:
        with vm(test.REPO_PATH, cleanup=not args.keep):
            input("Marginalia test VM started on 192.168.121.140. The username is deploy. Press enter to destroy it.")
    finally:
        if args.keep:
            print("Remember to run `vagrant destroy` in the tests directory to clean up the VM")
