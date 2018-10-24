#!/usr/bin/python3
from pathlib import Path
import subprocess
from contextlib import contextmanager
from tempfile import TemporaryDirectory
import urllib.request
from collections import namedtuple

import lib
from lib import vm, ansible, vagrant

REPO_PATH = Path(__file__).absolute().parent.parent


class TestError(Exception): pass

def assert_file(path):
    if not path.is_file():
        raise TestError("{} is not a file".format(path))

def assert_eq(a, b):
    if not a == b:
        raise TestError("{!r} is not equal to {!r}".format(a, b))

def test_html_static(ctx):
    resp = urllib.request.urlopen('http://{addr}/index.html'.format(addr=ctx['vm_addr']))
    assert_eq(resp.status, 200)
    # FIXME: add test to use dummy site and compare content

def test_api(ctx):
    try:
        urllib.request.urlopen('http://{addr}/api/'.format(addr=ctx['vm_addr']))
    except HttpError as e:
        assert_eq(e.code, 400)
    except Error as e:
        raise TestError("Unexpected error {}".format(e))
    else:
        raise TestError("No error")

@contextmanager
def vm_ctx(ctx):
    with vm(ctx['repo_path']):
        c2 = dict(ctx) 
        c2.update({'vm_addr': '192.168.121.140'})
        yield c2

def test_install(ctx):
    with open(ctx['repo_path'].joinpath('tests/ansible_inventory.ini')) as inv:
        inv_contents = inv.read()
    inv_path = ctx['tempdir'].joinpath('ansible_inventory.ini')
    with open(inv_path, 'w') as inv:
        inv.write(inv_contents.format(dist_path=ctx['tempdir'].joinpath('sdist')))

    try:
        vagrant('up', cwd=ctx['repo_path'].joinpath('tests')) # may leave an unprovisioned VM
        ansible('ansible/fresh.yml', inv_path, cwd=ctx['repo_path'])
        ansible('ansible/hosting.yml', inv_path, cwd=ctx['repo_path'])
        ansible('ansible/site2.yml', inv_path, cwd=ctx['repo_path'])
    finally:
        vagrant('destroy', cwd=ctx['repo_path'].joinpath('tests'))

@contextmanager
def sdist_ctx(ctx):
    lib.setup_sdist(ctx['repo_path'], ctx['tempdir'])
    yield ctx

def test_sdist(ctx):
    subprocess.run(['python3', 'setup.py', 'sdist',
            '--dist-dir', ctx['tempdir'].joinpath('sdist')],
        cwd=ctx['repo_path'], check=True)
    assert_file(ctx['tempdir'].joinpath('sdist/Marginalia-0.1.tar.gz'))

@contextmanager
def standard_ctx(ctx):
    yield ctx

@contextmanager
def get_test_context(repo_path):
    with TemporaryDirectory() as d:
        yield {'tempdir': Path(d),
               'repo_path': repo_path}


"""Ctxmgr is a context manager within which all tests in the suite will get executed"""
Suite = namedtuple('Suite', ['ctxmgr', 'tests'])

suites = (Suite(standard_ctx, [test_sdist]),
          Suite(sdist_ctx, [test_install]),
          Suite(vm_ctx, (test_html_static, test_api)))

def find_tests(suites, name):
    def find_suite_tests(tests, name):
        return [test for test in tests if test.__name__ == name]

    for setup_mgr, tests in suites:
        found_tests = find_suite_tests(tests, name)
        if found_tests:
            yield Suite(setup_mgr, found_tests)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('match', nargs='?', help='match test name')
    args = parser.parse_args()
    if args.match:
        suites = find_tests(tests, args.match)
    for setup_mgr, tests in suites:
        with get_test_context(REPO_PATH) as ctx:
            with setup_mgr(ctx) as ctx:
                for test in tests:
                    test(ctx)
