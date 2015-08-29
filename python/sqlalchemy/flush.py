# -*- coding: utf-8 -*-

from sqlalchemy import (
    create_engine,
    Column,
    CHAR,
    Integer,
    String,
)
from sqlalchemy.orm import (
    sessionmaker,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String(50))
    password = Column(String(30))

    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)


if __name__ == "__main__":
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 测试在不自动刷新的情况下flush的功能
    session = Session()
    session.autoflush = False
    user = User('ed', 'Ed Jones', 'password')
    session.add(user)
    rows = session.query(User).filter(User.name == 'ed').all()
    print 'added to session, not flushed, equal to 0', len(rows)
    session.flush()
    rows = session.query(User).filter(User.name == 'ed').all()
    print 'flushed, equal to 1', len(rows)
    session.rollback()
    rows = session.query(User).filter(User.name == 'ed').all()
    print 'rollback, equal to 0', len(rows)
