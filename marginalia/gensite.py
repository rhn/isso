#! /usr/bin/python3
import os.path
from pathlib import Path
import itertools
from collections import ChainMap
import warnings

import CommonMark
import yaml

from jinja2 import Template
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def split_content(text):
    lines = text.splitlines()
    def is_delim(line):
        return line.rstrip() == '---'

    if not is_delim(lines[0]):
        return None, text

    lines = iter(lines[1:]) # removes opening
    meta = '\n'.join(itertools.takewhile(lambda x: not is_delim(x), lines)) # this strips the delimiter
    content = '\n'.join(list(lines))
    return meta, content


def parse_content(text):
    meta_str, content_str = split_content(text)
    meta = None if meta_str is None else yaml.load(meta_str)
    content_html = CommonMark.commonmark(content_str)
    return meta, content_html


def make_page(config, env, text, template_filename):
    """take doc name and derive from there"""
    template = env.get_template(template_filename)
    meta, content = parse_content(text.read_text())
    return template.render(ChainMap({'meta': meta,
                                     'content': content},
                                    config))


def update_entry(config, book_path):
    print("FIXME: add to db")
    return {"number": -1,
            "photos": []}

def generate(srcpath, dstpath):
    templates = os.path.join(srcpath, 'templates')
    env = Environment(
        loader=FileSystemLoader(templates),
        autoescape=True,
        extensions=['jinja2.ext.autoescape'],
        undefined=StrictUndefined
    )
    config = yaml.load(open(os.path.join(srcpath, 'config.yaml')).read())
    contents = os.path.join(srcpath, 'contents')
    templates = os.path.join(srcpath, 'templates')
    books = os.path.join(srcpath, 'books')

    for root, dirs, files in os.walk(contents):
        relroot = os.path.relpath(root, contents)
        dstroot = os.path.join(dstpath, relroot)

        for dirname in dirs:
            os.makedirs(os.path.join(dstroot, dirname), exist_ok=True)

        for fname in files:
            name = os.path.splitext(fname)[0]
            templ_name = name + '.html'
            page = make_page(config, env, Path(root, fname), templ_name)
            if templ_name == "index.html":
                dest_name = templ_name
            else:
                os.makedirs(os.path.join(dstroot, name), exist_ok=True)
                dest_name = os.path.join(name, 'index.html')
            with open(os.path.join(dstroot, dest_name), 'w') as f:
                f.write(page)


    for d in Path(books).iterdir():
        if not d.is_dir():
            warnings.warn("{} is in books/ but not a directory...".format(d))
            continue

        name_slug = d.name
        dstdir = Path(dstroot, config["book_path"], name_slug)
        dstdir.mkdir(exist_ok=True)
        meta = update_entry(config, dstdir)
        book_config = ChainMap({"journal": meta}, config)

        for fpath in d.iterdir():
            name = fpath.stem
            
            page = make_page(book_config, env, fpath, 'journal.html')
            dstdir.joinpath(name + '.html').write_text(page)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("sourcepath")
    args = parser.parse_args()
    generate(args.sourcepath, '.')
