# -*- coding: utf-8 -*-

import simplejson as json

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import (
    sessionmaker,
    relationship,
    backref,
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


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    email_address = Column(String(120), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))  # 外键定义
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

    ed_user = User('ed', 'Ed Jones', 'password')
    session.add(ed_user)
    session.commit()

    jack_user = User('jack', 'Jack Bean', 'gjffdd')
    jack_user.addresses = [Address(email_address='jack@google.com'), Address(email_address='j25@yahoo.com')]
    session.add(jack_user)
    session.commit()

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
