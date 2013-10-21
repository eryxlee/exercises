# -*- coding: utf-8 -*-

# https://github.com/ghosert/VimProject/blob/master/StudyPyramid/sql_alchemy

import unittest

from pyramid import testing

from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Text,

    ForeignKey,

    func,
    and_,
    or_
    )
from sqlalchemy.orm.exc import (
    MultipleResultsFound,
    NoResultFound,
    )
from sqlalchemy.orm import (
    relationship,
    backref,
    aliased,
    )
from sqlalchemy.sql import exists
from sqlalchemy.ext.declarative import declarative_base

_skip_test = True   # 测试控制，方便开发时忽略不关注的测试用例
Base = declarative_base()


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, email_address):
        self.email_address = email_address

    def __repr__(self):
        return "<Address('%s')>" % self.email_address


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    addresses = relationship(Address,  order_by="Address.id", backref=backref('user'), cascade="all, delete, delete-orphan")

    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password
    def __repr__(self):
       return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)


# 多对多关系需要的中间表不能定义成class，这种表在系统使用过程中基本不可见
post_keywords = Table('post_keywords', Base.metadata,
                      Column('post_id', Integer, ForeignKey('posts.id')),
                      Column('keyword_id', Integer, ForeignKey('keywords.id'))
)


class BlogPost(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    headline = Column(String(255), nullable=False)
    body = Column(Text)

    # many to many BlogPost<->Keyword
    keywords = relationship('Keyword', secondary=post_keywords, backref='posts')

    author = relationship(User, backref=backref('posts', lazy='dynamic'))

    def __init__(self, headline, body, author):
        self.author = author
        self.headline = headline
        self.body = body

    def __repr__(self):
        return "BlogPost(%r, %r, %r)" % (self.headline, self.body, self.author)


class Keyword(Base):
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key=True)
    keyword = Column(String(50), nullable=False, unique=True)

    def __init__(self, keyword):
        self.keyword = keyword


class TestSQLAlchemy(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite:///:memory:', echo=True)

        Base.metadata.create_all(engine)

        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.ed_user = User('ed', 'Ed Jones', 'edspassword')
        self.session.add(self.ed_user)
        self.session.commit()

    def tearDown(self):
        testing.tearDown()

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_delete_cascade(self):
        jack = User('jack', 'Jack Bean', 'gjffdd')
        jack.addresses = [Address(email_address='jack@google.com'), Address(email_address='j25@yahoo.com'), Address(email_address='jane@163.com')]
        self.session.add(jack)
        self.session.commit()

        # 载入User，Address延迟载入
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name = ?
        # ('jack',)
        user = self.session.query(User).filter(User.name=='jack').one()

        # 访问Address的时候才载入Address信息，但删除的时候并不是马上发出Delete语句进行删除，而是需要等待下一句查询发出后才真实发出Delete
        # SELECT addresses.id AS addresses_id, addresses.email_address AS addresses_email_address, addresses.user_id AS addresses_user_id
        # FROM addresses
        # WHERE ? = addresses.user_id ORDER BY addresses.id
        # (2,)
        del user.addresses[1]

        # 下一个查询语句执行前执行Delete动作
        # DELETE FROM addresses WHERE addresses.id = ?
        # (2,)
        # SELECT count(*) AS count_1
        # FROM (SELECT addresses.id AS addresses_id, addresses.email_address AS addresses_email_address, addresses.user_id AS addresses_user_id
        # FROM addresses
        # WHERE addresses.email_address IN (?, ?)) AS anon_1
        # ('jack@google.com', 'j25@yahoo.com', 'jane@163.com')
        count = self.session.query(Address).filter(Address.email_address.in_(['jack@google.com', 'j25@yahoo.com', 'jane@163.com'])).count()
        self.assertTrue(count == 2)

        # DELETE FROM addresses WHERE addresses.id = ?
        # ((1,), (3,))
        # DELETE FROM users WHERE users.id = ?
        # (2,)
        # SELECT count(*) AS count_1
        # FROM (SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name = ?) AS anon_1
        # ('jack',)
        self.session.delete(user)
        count = self.session.query(User).filter(User.name=='jack').count()
        self.assertTrue(count == 0)


    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_many_to_many(self):
        self.session.add_all([
            User('wendy', 'Wendy Williams', 'foobar'),
            User('mary', 'Mary Contrary', 'xxg527'),
            User('fred', 'Fred Flinstone', 'blah')
        ])

        wendy = self.session.query(User).filter_by(name='wendy').one()

        post = BlogPost("Wendy's Blog Post", "This is a test", wendy)
        self.session.add(post)

        post.keywords.append(Keyword('wendy'))
        post.keywords.append(Keyword('firstpost'))

        # SELECT posts.id AS posts_id, posts.user_id AS posts_user_id, posts.headline AS posts_headline, posts.body AS posts_body
        # FROM posts
        # WHERE EXISTS (SELECT 1
        # FROM post_keywords, keywords
        # WHERE posts.id = post_keywords.post_id AND keywords.id = post_keywords.keyword_id AND keywords.keyword = ?)
        # ('firstpost',)
        posts = self.session.query(BlogPost).filter(BlogPost.keywords.any(keyword='firstpost')).all()
        self.assertTrue(posts[0].headline == "Wendy's Blog Post")
        self.assertTrue(posts[0].author.name == 'wendy')

        # SELECT posts.id AS posts_id, posts.user_id AS posts_user_id, posts.headline AS posts_headline, posts.body AS posts_body
        # FROM posts
        # WHERE ? = posts.user_id AND (EXISTS (SELECT 1
        # FROM post_keywords, keywords
        # WHERE posts.id = post_keywords.post_id AND keywords.id = post_keywords.keyword_id AND keywords.keyword = ?))
        # (2, 'firstpost')
        posts = self.session.query(BlogPost).filter(BlogPost.author==wendy).filter(BlogPost.keywords.any(keyword='firstpost')).all()
        self.assertTrue(posts[0].headline == "Wendy's Blog Post")
        self.assertTrue(posts[0].author.name == 'wendy')

        # SELECT posts.id AS posts_id, posts.user_id AS posts_user_id, posts.headline AS posts_headline, posts.body AS posts_body
        # FROM posts
        # WHERE ? = posts.user_id AND (EXISTS (SELECT 1
        # FROM post_keywords, keywords
        # WHERE posts.id = post_keywords.post_id AND keywords.id = post_keywords.keyword_id AND keywords.keyword = ?))
        # (2, 'firstpost')
        posts = wendy.posts.filter(BlogPost.keywords.any(keyword='firstpost')).all()
        self.assertTrue(posts[0].headline == "Wendy's Blog Post")
        self.assertTrue(posts[0].author.name == 'wendy')

