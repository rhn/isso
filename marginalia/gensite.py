#! /usr/bin/python3
import os.path
import itertools
from collections import ChainMap

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
    meta = ''.join(itertools.takewhile(is_delim, lines)) # this strips the delimiter
    content = ''.join(list(lines))
    return meta, content


def parse_content(text):
    meta_str, content_str = split_content(text)
    meta = None if meta_str is None else yaml.load(meta_str)
    content_html = CommonMark.commonmark(content_str)
    return meta, content_html


def make_page(config, env, text, template_filename):
    """take doc name and derive from there"""
    template = env.get_template(template_filename)
    meta, content = parse_content(open(text).read())
    return template.render(ChainMap({'meta': meta,
                                     'content': content},
                                    config))


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

    for root, dirs, files in os.walk(contents):
        relroot = os.path.relpath(root, contents)
        dstroot = os.path.join(dstpath, relroot)

        for dirname in dirs:
            os.makedirs(os.path.join(dstroot, dirname), exist_ok=True)

        for fname in files:
            name = os.path.splitext(fname)[0]
            templ_name = name + '.html'
            page = make_page(config, env, os.path.join(root, fname), templ_name)
            if templ_name == "index.html":
                dest_name = templ_name
            else:
                os.makedirs(os.path.join(dstroot, name), exist_ok=True)
                dest_name = os.path.join(name, 'index.html')
            with open(os.path.join(dstroot, dest_name), 'w') as f:
                f.write(page)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("destpath")
    args = parser.parse_args()
    generate('.', args.destpath)
