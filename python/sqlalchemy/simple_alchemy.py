# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    func,
    and_,
    or_
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
    # from_ = Column('from', CHAR(10))   # 如果字段名跟python关键字冲突，后面加_
    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password
    def __repr__(self):
       return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)


class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String(120), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))    # 外键定义
    user = relationship(User, backref=backref('addresses', order_by=id))
    def __init__(self, email_address):
        self.email_address = email_address
    def __repr__(self):
        return "<Address('%s')>" % self.email_address


engine = create_engine('sqlite:///:memory:', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

ed_user = User('ed', 'Ed Jones', 'password')
session.add(ed_user)
session.commit()

jack = User('jack', 'Jack Bean', 'gjffdd')
jack.addresses = [Address(email_address='jack@google.com'), Address(email_address='j25@yahoo.com')]
session.add(jack)
session.commit()


rows = session.query(User, Address)\
    .filter(User.id==Address.user_id)\
    .filter(Address.email_address=='jack@google.com')\
    .all()

rows = session.query(User.id.label('id'), User.name.label('name'), Address.email_address.label('email'))\
    .filter(User.id==Address.user_id)\
    .filter(Address.email_address=='jack@google.com')\
    .all()

import simplejson as json
print json.dumps(rows, namedtuple_as_object=True)
#'[{"email": "jack@google.com", "id": 1, "name": "jack"}]'


session.query(Address).delete()
session.query(User).delete()
session.commit()


session = Session()
session.autoflush = False
user = User('ed', 'Ed Jones', 'password')
session.add(user)
rows = session.query(User).filter(User.name=='ed').all()
print 'added to session, not flushed, equal to 0', len(rows)
session.flush()
rows = session.query(User).filter(User.name=='ed').all()
print 'flushed, equal to 1', len(rows)
session.rollback()
rows = session.query(User).filter(User.name=='ed').all()
print 'rollback, equal to 0', len(rows)

