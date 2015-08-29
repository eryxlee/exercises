# -*- coding: utf-8 -*-

import simplejson as json

from sqlalchemy import (
    create_engine,
    event,
    Table,
    Column,
    CHAR,
    Integer,
    String,
    ForeignKey,
    func,
    and_,
    or_,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import (
    relationship,
    backref,
    aliased,
    joinedload,
    contains_eager,
)
from sqlalchemy.orm.exc import (
    MultipleResultsFound,
    NoResultFound,
)
from sqlalchemy.sql import exists
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String(120))
    password = Column(String(30))
    from_ = Column('from', CHAR(10))   # 如果字段名跟python关键字冲突，后面加_; 字段名跟属性名字不一致要分别指定。

    def __init__(self, name, fullname, password, from_):
        self.name = name
        self.fullname = fullname
        self.password = password
        self.from_ = from_

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    email_address = Column(String(120), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))  # 外键定义
    user = relationship(User, backref=backref('addresses', order_by=id))

    def __init__(self, email_address):
        self.email_address = email_address

    def __repr__(self):
        return "<Address('%s')>" % self.email_address


if __name__ == "__main__":
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    ed_user = User('ed', 'Ed Jones', 'password', 'china')
    session.add(ed_user)
    session.commit()

    jack = User('jack', 'Jack Bean', 'gjffdd', 'usa')
    jack.addresses = [Address(email_address='jack@google.com'), Address(email_address='j25@yahoo.com')]
    session.add(jack)
    session.commit()

    # 取出部分字段的内容，这是sqlalchemy会输出一个包含多个tuple的list
    stmt = session.query(User.id, User.name, User.from_) \
        .filter(User.name == 'jack')
    tuple_rows = stmt.all()

    # 如果类属性名跟字段名不一致，那么key, name 分别代表这两个值，注意这个区别
    print [User.id.key, User.name.key, User.from_.key]
    # ['id', 'name', 'from_']
    print [col.get("name") for col in stmt.column_descriptions]
    # ['id', 'name', 'from_']
    print [User.id.name, User.name.name, User.from_.name]
    # ['id', 'name', 'from']

    # 如果在输出前要修改转化其中的内容，可以转换成dict来使用
    print [r._asdict() for r in tuple_rows]
    # [{'from_': u'usa', 'id': 2, 'name': u'jack'}]

    # 如果直接输出JSON，可以不用转换成dict，直接使用namedtuple_as_object
    print json.dumps(tuple_rows, namedtuple_as_object=True)
    # [{"from_": "usa", "id": 2, "name": "jack"}]

    rows = session.query(User.id.label('id'), User.name.label('name'), Address.email_address.label('email')) \
        .filter(User.id == Address.user_id) \
        .filter(Address.email_address == 'jack@google.com') \
        .all()

    print json.dumps(rows, namedtuple_as_object=True)
    # '[{"email": "jack@google.com", "id": 1, "name": "jack"}]'

    # 删除两个表中的数据
    session.query(Address).delete()
    session.query(User).delete()
    session.commit()

    # 测试在不自动刷新的情况下flush的功能
    session = Session()
    session.autoflush = False
    user = User('ed', 'Ed Jones', 'password', 'china')
    session.add(user)
    rows = session.query(User).filter(User.name == 'ed').all()
    print 'added to session, not flushed, equal to 0', len(rows)
    session.flush()
    rows = session.query(User).filter(User.name == 'ed').all()
    print 'flushed, equal to 1', len(rows)
    session.rollback()
    rows = session.query(User).filter(User.name == 'ed').all()
    print 'rollback, equal to 0', len(rows)
