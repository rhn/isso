from contextlib import contextmanager

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
 
 
Base = declarative_base()


class Thread(Base):
    __tablename__ = 'threads'
    id = Column(Integer, primary_key=True)
    uri = Column(String, unique=True)
    title = Column(String)
    date_added = Column(Date)
# TODO: add metadata from template file

@contextmanager
def session(path):
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///{}'.format(path))
     
    from sqlalchemy.orm import sessionmaker
    sessionm = sessionmaker()
    sessionm.configure(bind=engine)
    Base.metadata.create_all(engine)
    s = sessionm()
    yield s
    s.commit()
