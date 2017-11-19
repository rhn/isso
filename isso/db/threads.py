# -*- encoding: utf-8 -*-

from . import schema

def Thread(id, uri, title, *args):
    return {
        "id": id,
        "uri": uri,
        "title": title,
    }


class Threads(object):

    def __init__(self, db):
        self.db = db

    def __contains__(self, uri):
        return self.db.execute("SELECT title FROM threads WHERE uri=?", (uri, )) \
                      .fetchone() is not None

    def __getitem__(self, uri):
        return Thread(*self.db.execute("SELECT * FROM threads WHERE uri=?", (uri, )).fetchone())

    def new(self, uri, title):
        self.db.execute("INSERT INTO threads (uri, title) VALUES (?, ?)", (uri, title))
        return self[uri]
    
    def get_all(self):
        return (Thread(*item) for item in self.db.execute("SELECT * FROM threads"))
