import os.path
import itertools

import CommonMark
import yaml
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader


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


# take doc name and derive from there
def make_index(config, env, text):
    template = env.get_template('index.html')
    meta, content = parse_content(open(text).read())
    return template.render({'meta': meta,
                            'content': content})


def generate(srcpath, dstpath):
    templates = os.path.join(srcpath, 'templates')
    env = Environment(
        loader=FileSystemLoader(templates),
        autoescape=True,
        extensions=['jinja2.ext.autoescape']
    )
    config = yaml.load(open(os.path.join(srcpath, 'config.yaml')).read())
    contents = os.path.join(srcpath, 'contents')
    indexpage = make_index(config, env, os.path.join(contents, 'index.md'))
    with open(os.path.join(dstpath, 'index.html'), 'w') as f:
        f.write(indexpage)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("destpath")
    args = parser.parse_args()
    generate('.', args.destpath)
