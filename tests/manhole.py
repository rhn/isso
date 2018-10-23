import test
from lib import vm


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
