import test

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', nargs='?', default='marginalia',
        choices=('user', 'nginx', 'marginalia'),
        help='Stage to which the VM should be installed')
    parser.add_argument('--keep', action='store_true', help='Keep the VM if creation fails')
    args = parser.parse_args()

    stage_enum = test.VMStage.from_string(args.stage)
    print("Creating Marginalia VM up to the stage {}".format(stage_enum))
    try:
        with test.vm(test.REPO_PATH, install_stage=stage_enum, cleanup=not args.keep):
            input("Marginalia test VM started on 192.168.121.140. The username is deploy. Press enter to destroy it.")
    finally:
        if args.keep:
            print("Remember to run `vagrant destroy` in the tests directory to clean up the VM")
