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
    first_name = Column(String(30))
    last_name = Column(String(50))
    password = Column(String(30))

    def __init__(self, first_name, last_name, password):
        self.first_name = first_name
        self.last_name = last_name
        self.password = password

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.first_name, self.last_name, self.password)


if __name__ == "__main__":
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 测试在不自动刷新的情况下flush的功能
    session = Session()
    session.autoflush = False
    user = User('Ed', 'Jones', 'password')
    session.add(user)
    rows = session.query(User).filter(User.first_name == 'Ed').all()
    print 'added to session, not flushed, equal to 0', len(rows)
    session.flush()
    rows = session.query(User).filter(User.first_name == 'Ed').all()
    print 'flushed, equal to 1', len(rows)
    session.rollback()
    rows = session.query(User).filter(User.first_name == 'Ed').all()
    print 'rollback, equal to 0', len(rows)
