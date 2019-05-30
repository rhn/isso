#!/usr/bin/python3
from pathlib import Path
import subprocess
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
import urllib.request
from collections import namedtuple
import shutil
from glob import glob

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

def sum_dict(d, e):
    d2 = dict(d)
    d2.update(e)
    return d2

def test_lib_replace(ctx):
    ini = """[marginalia]
192.168.121.140

[marginalia:vars]
book_path=book
post_path=post
db_path=/srv/marginalia/data/comments.db
host_site_path=../tests/site/
host_bookcodes_path={bookcodes_path}
host_dist_path={dist_path}"""
    assert_eq(lib.replace_ini(ini, "host_site_path", "foo"),
        """[marginalia]
192.168.121.140

[marginalia:vars]
book_path=book
post_path=post
db_path=/srv/marginalia/data/comments.db
host_site_path=foo
host_bookcodes_path={bookcodes_path}
host_dist_path={dist_path}""")

def test_install(ctx):
    with open(ctx['repo_path'].joinpath('tests/ansible_inventory.ini')) as inv:
        inv_contents = inv.read()
    inv_path = ctx['tempdir'].joinpath('ansible_inventory.ini')
    bookcodes_path = ctx['tempdir'].joinpath('bookcodes')
    with open(inv_path, 'w') as inv:
        inv.write(inv_contents.format(
            dist_path=ctx['tempdir'].joinpath('sdist'),
            bookcodes_path=bookcodes_path))
    lib.try_mkdir(bookcodes_path)
    try:
        vagrant('up', cwd=ctx['repo_path'].joinpath('tests')) # may leave an unprovisioned VM
        ansible('ansible/fresh.yml', inv_path, cwd=ctx['repo_path'])
        ansible('ansible/hosting.yml', inv_path, cwd=ctx['repo_path'])
        ansible('ansible/users.yml', inv_path, cwd=ctx['repo_path'])
        ansible('ansible/site2.yml', inv_path, cwd=ctx['repo_path'])
    finally:
        vagrant('destroy', cwd=ctx['repo_path'].joinpath('tests'))

@contextmanager
def sdist_ctx(ctx):
    sdist_path = lib.setup_sdist(ctx['repo_path'], ctx['tempdir'])
    yield sum_dict(ctx, {'sdist_path': sdist_path})

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

@contextmanager
def vm_ctx(ctx):
    with vm(ctx['repo_path']) as data:
        yield sum_dict(ctx, data)

def test_html_static(ctx):
    resp = urllib.request.urlopen('http://{addr}/index.html'.format(addr=ctx['vm_addr']))
    assert_eq(resp.status, 200)
    # FIXME: add test to use dummy site and compare content

def test_api(ctx):
    try:
        urllib.request.urlopen('http://{addr}/api/'.format(addr=ctx['vm_addr']))
    except HTTPError as e:
        assert_eq(e.code, 400)
    except Error as e:
        raise TestError("Unexpected error {}".format(e))
    else:
        raise TestError("No error")

def read_codes(d):
    return dict((Path(f).name, open(f).read()) for f
                in glob(d.as_posix() + '/*.txt'))

def test_vm_add_book(ctx):
    """
    Just copies the book into the site/books dir and runs site2.yml again.
    All the hassle is to compare the before/after bookcodes.
    """
    with open(ctx['repo_path'].joinpath('tests/ansible_inventory.ini')) as inv:
        inv_contents = inv.read()
    with TemporaryDirectory() as td:
        site = Path(td).joinpath('site')
        shutil.copytree(ctx['repo_path'].joinpath('tests/site'), site)
        inv_contents = lib.replace_ini(inv_contents, 'host_site_path', site.as_posix())

        bookcodes_path = Path(td).joinpath('bookcodes')
        lib.try_mkdir(bookcodes_path)
        inv_path = Path(td).joinpath('ansible_inventory.ini')
        with open(inv_path, 'w') as inv:
            inv.write(inv_contents.format(dist_path=ctx['sdist_path'],
                bookcodes_path=bookcodes_path))

        # save existing bookcodes
        ansible('ansible/site2.yml', inv_path, cwd=ctx['repo_path'])
        pre_codes = read_codes(bookcodes_path.joinpath(ctx['vm_addr']))

        # copy the new book into the site (temporry, don't pollute the repo)
        shutil.copytree(ctx['repo_path'].joinpath('tests/test_book'), site.joinpath('books/test_book'))

        # apply the new book change
        try:
            ansible('ansible/site2.yml', inv_path, cwd=ctx['repo_path'])
        except:
            import traceback
            traceback.print_exc()
            input()
            raise

        post_codes = read_codes(bookcodes_path.joinpath(ctx['vm_addr']))
        new_entries = set(post_codes.keys()) - set(pre_codes.keys())

        assert_eq(len(new_entries), 1)
        
        post_codes.pop(new_entries.pop())
        assert_eq(pre_codes, post_codes)


@contextmanager
def ctx_gen_venv(ctx):
    venvdir = ctx['tempdir'].joinpath('venv')
    subprocess.run(['python3', '-m', 'venv', venvdir], check=True)
    subprocess.run([venvdir.joinpath('bin/python3').as_posix(),
                    '-m', 'pip', 'install',
                    '-r', ctx['repo_path'].joinpath('marginalia/requirements.txt').as_posix()],
                   check=True)
    yield sum_dict(ctx, {'gen_venvdir': venvdir})


@contextmanager
def make_html_database(ctx):
    """Makes both html and db in a temporary directory"""
    with open(ctx['repo_path'].joinpath('tests/site/config.yaml.native')) as config:
        config_contents = config.read()
    with TemporaryDirectory() as td:
        db_path = Path(td).joinpath('comments.db')
        site = Path(td).joinpath('site')
        html = Path(td).joinpath('html')
        lib.try_mkdir(html)
        bookcodes = Path(td).joinpath('codes')
        lib.try_mkdir(bookcodes)
        shutil.copytree(ctx['repo_path'].joinpath('tests/site'), site)
        conf_path = site.joinpath('config.yaml')
        with open(conf_path, 'w') as conf:
            conf.write(config_contents.format(db_path=db_path))
        
        subprocess.run([ctx['gen_venvdir'].joinpath('bin/python3').as_posix(),
                        ctx['repo_path'].joinpath('marginalia/gensite.py').as_posix(),
                        site.as_posix()],
                       cwd=html, check=True)
        yield td


def test_gen_html(ctx):
    with open(ctx['repo_path'].joinpath('tests/site/config.yaml.native')) as config:
        config_contents = config.read()
    with TemporaryDirectory() as td:
        db_path = Path(td).joinpath('comments.db')
        site = Path(td).joinpath('site')
        html = Path(td).joinpath('html')
        lib.try_mkdir(html)
        shutil.copytree(ctx['repo_path'].joinpath('tests/site'), site)
        conf_path = site.joinpath('config.yaml')
        with open(conf_path, 'w') as conf:
            conf.write(config_contents.format(db_path=db_path))
        
        subprocess.run([ctx['gen_venvdir'].joinpath('bin/python3').as_posix(),
                        ctx['repo_path'].joinpath('marginalia/gensite.py').as_posix(),
                        site],
                       cwd=html, check=True)


def test_gen_code(ctx):
    with make_html_database(ctx) as td:
        site = Path(td).joinpath('site')
        bookcodes = Path(td).joinpath('codes')
        subprocess.run([ctx['gen_venvdir'].joinpath('bin/python3').as_posix(),
                        ctx['repo_path'].joinpath('marginalia/genlabel.py').as_posix(),
                        site.as_posix(), bookcodes.as_posix()],
                       check=True)


def test_add_book(ctx):
    with make_html_database(ctx) as td:
        site = Path(td).joinpath('site')
        html = Path(td).joinpath('html')
        bookcodes = Path(td).joinpath('codes')
        subprocess.run([ctx['gen_venvdir'].joinpath('bin/python3').as_posix(),
                        ctx['repo_path'].joinpath('marginalia/genlabel.py').as_posix(),
                        site.as_posix(), bookcodes.as_posix()],
                       check=True)
        pre_codes = read_codes(bookcodes)

        shutil.copytree(ctx['repo_path'].joinpath('tests/test_book'), site.joinpath('books/test_book'))

        subprocess.run([ctx['gen_venvdir'].joinpath('bin/python3').as_posix(),
                        ctx['repo_path'].joinpath('marginalia/gensite.py').as_posix(),
                        site.as_posix()],
                       cwd=html, check=True)
        subprocess.run([ctx['gen_venvdir'].joinpath('bin/python3').as_posix(),
                        ctx['repo_path'].joinpath('marginalia/genlabel.py').as_posix(),
                        site.as_posix(), bookcodes.as_posix()],
                       check=True)

        post_codes = read_codes(bookcodes)
        new_entries = set(post_codes.keys()) - set(pre_codes.keys())
        assert_eq(len(new_entries), 1)
        
        post_codes.pop(new_entries.pop())
        assert_eq(pre_codes, post_codes)


"""Ctxmgr is a context manager within which all tests in the suite will get executed"""
Suite = namedtuple('Suite', ['name', 'ctxmgr', 'tests'])

suites = (Suite("", standard_ctx, [test_lib_replace]),
          Suite("", standard_ctx, [test_sdist]),
          Suite("install", sdist_ctx, [test_install]),
          Suite("vm", vm_ctx, (test_html_static, test_api, test_vm_add_book)),
          Suite("venv", ctx_gen_venv, [test_gen_html, test_gen_code, test_add_book]))

def find_tests(suites, match):
    def find_suite_tests(tests, name):
        return [test for test in tests if test.__name__ == name]

    for name, setup_mgr, tests in suites:
        if match not in name:
            tests = find_suite_tests(tests, name)
        if tests:
            yield Suite(name, setup_mgr, tests)


def perform_tests(suites):
    for suite_name, setup_mgr, tests in suites:
        print("Starting suite", suite_name)
        with get_test_context(REPO_PATH) as ctx:
            with setup_mgr(ctx) as ctx:
                for test in tests:
                    print("running", suite_name, test.__name__)
                    try:
                        test(ctx)
                    except Exception as e:
                        traceback.print_exc(e)
                        result = 'fail'
                    else:
                        result = 'pass'
                    finally:
                        yield suite_name, test.__name__, result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('match', nargs='?', help='match test name')
    args = parser.parse_args()
    if args.match:
        suites = find_tests(suites, args.match)
    results = list(perform_tests(suites))
    for suite, test, result in results:
        print(suite, test, result)
