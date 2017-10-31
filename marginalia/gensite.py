#! /usr/bin/python3
import os.path
from pathlib import Path
import itertools
from collections import ChainMap
import warnings
from contextlib import contextmanager
import random
random.seed()
import string
from datetime import date, datetime

import CommonMark
import yaml

from jinja2 import Template
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
 
 
Base = declarative_base()
# TODO: move to core
# TODO: migration with alembic

class Thread(Base):
    __tablename__ = 'threads'
    id = Column(Integer, primary_key=True)
    uri = Column(String, unique=True)
    title = Column(String)
    date_added = Column(Date)
# TODO: add metadata from template file


class Access(Base):
    __tablename__ = 'access'
    id = Column(Integer, primary_key=True)
    uri = Column(String, unique=True)
    key = Column(String)


@contextmanager
def open_db(path):
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///{}'.format(path))
     
    from sqlalchemy.orm import sessionmaker
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)
    s = session()
    yield s
    s.commit()


def make_token(n):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(n))


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


def update_entry(config, book_slug, book_path):
    """Check if book exists, and add to database"""
    contents_path = book_path.joinpath("index.md")
    meta, content = parse_content(contents_path.read_text())

    with open_db(config["db_path"]) as session:
        thread = session.query(Thread).filter(Thread.uri == book_slug).one_or_none()
        if thread is None:
            thread = Thread(title=meta['title'],
                            uri=book_slug,
                            date_added=meta['date'])
            session.add(thread)
        access = session.query(Access).filter(Access.uri == book_slug).one_or_none()
        if access is None:
            access = Access(uri=book_slug, key=make_token(8))
            session.add(access)
            print("Key for {} is {}".format(thread.title, access.key))
        session.commit()    
        
        return {"number": access.id,
                "code": access.key,
                "slug": book_slug,
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

        meta = update_entry(config, name_slug, d)

        postdir = Path(dstroot, config["post_path"], meta['code'])
        postdir.parent.mkdir(exist_ok=True)
        postdir.mkdir(exist_ok=True)

        book_config = ChainMap({"journal": meta}, config)
        
        for fpath in d.iterdir():
            name = fpath.stem
            page = make_page(book_config, env, fpath, 'journal.html')
            dstdir.joinpath(name + '.html').write_text(page)
            
            page = make_page(book_config, env, fpath, 'journal_post.html')
            postdir.joinpath(name + '.html').write_text(page)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("sourcepath")
    args = parser.parse_args()
    generate(args.sourcepath, '.')
