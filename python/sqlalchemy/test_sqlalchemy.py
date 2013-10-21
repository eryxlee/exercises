# -*- coding: utf-8 -*-

# some examples from bellowing link
# https://github.com/ghosert/VimProject/blob/master/StudyPyramid/sql_alchemy

import unittest

from pyramid import testing

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

_skip_test = True   # 测试控制，方便开发时忽略不关注的测试用例
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {              # 单独设置数据库参数，MYSQL有效
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
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

    # 定义一个一对多的关系，在Address实例中，可以用user属性来引用User实例；在User实例中，可以
    # 使用addresses来引用Address列表
    user = relationship(User, backref=backref('addresses', order_by=id))

    def __init__(self, email_address):
        self.email_address = email_address

    def __repr__(self):
        return "<Address('%s')>" % self.email_address


class TestSQLAlchemy(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

        self.engine = create_engine('mysql://root:@127.0.0.1/test?charset=utf8', echo=True)
        # self.engine = create_engine('sqlite:///:memory:', echo=True)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.ed_user = User('ed', 'Ed Jones', 'password')
        self.session.add(self.ed_user)
        self.session.commit()

    def tearDown(self):
        self.session.query(Address).delete()
        self.session.query(User).delete()
        self.session.commit()
        # TODO MySQL中在drop table addresses时挂起，原因不明
        # Base.metadata.drop_all(self.engine, checkfirst=False)
        testing.tearDown()

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_schema(self):
        # 取得字段信息
        self.assertEqual(User.name.property.columns[0].type.length, 30)

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_new(self):
        self.assertTrue(len(self.session.new) == 0, '在新增前确保没有待写入的数据。')

        wendy = User('wendy', 'Wendy Williams', 'foobar')
        self.session.add(wendy)
        self.assertTrue(len(self.session.new) == 1, '新增一条数据后确保只有一条待写入的数据。')

        self.session.commit()
        self.assertTrue(len(self.session.new) == 0, '确保在commit后再没有待写入的数据。')

        self.session.add_all([
            User('mary', 'Mary Contrary', 'xxg527'),
            User('fred', 'Fred Flinstone', 'blah')
        ])
        self.assertTrue(len(self.session.new) == 2, '新增多条数据后确保有多个数据待写入。')

        self.session.commit()
        self.assertTrue(len(self.session.new) == 0, '确保在commit后再没有待写入的数据。')

        users = self.session.query(User).filter(User.name.in_(['wendy', 'mary', 'fred'])).all()
        self.assertTrue(len(users) == 3, '新增后确保取出来的就是插入的数据')

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_delete(self):
        wendy = User('wendy', 'Wendy Williams', 'foobar')
        mary = User('mary', 'Mary Contrary', 'xxg527')
        fred = User('fred', 'Fred Flinstone', 'blah')
        self.session.add_all([wendy, mary, fred ])
        self.session.commit()

        user = self.session.query(User).filter(User.name=='wendy').one()
        self.assertTrue(user.name == 'wendy', '在删除前确保数据已经存在。')
        self.session.delete(user)

        # DELETE FROM users WHERE users.id = ?
        # (2,)
        self.session.commit()
        self.assertTrue(user not in self.session, '确保删除数据已经不存在。')
        self.assertTrue(wendy not in self.session, '确保删除数据已经不存在。')
        with self.assertRaises(NoResultFound):
            self.session.query(User).filter(User.name=='wendy').one()

        # 另外一种删除方法，这种方式直接生成Delete SQL语句，不用先取出数据，也可以一次修改多个记录
        # DELETE FROM users WHERE users.name = ?
        # ('mary',)
        self.session.query(User).filter(User.name=='mary').delete()
        self.assertTrue(mary not in self.session)
        with self.assertRaises(NoResultFound):
            self.session.query(User).filter(User.name=='mary').one()

        fred.addresses = [Address(email_address='fred@google.com'), Address(email_address='fred@yahoo.com')]
        self.session.commit()
        # 生成如下SQL，如果需要删除address数据，需要在定义关系时加上CASCADE
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.id = ?
        # (4,)
        # SELECT addresses.id AS addresses_id, addresses.email_address AS addresses_email_address, addresses.user_id AS addresses_user_id
        # FROM addresses
        # WHERE ? = addresses.user_id ORDER BY addresses.id
        # (4,)
        # UPDATE addresses SET user_id=? WHERE addresses.id = ?
        # (None, 1)
        # UPDATE addresses SET user_id=? WHERE addresses.id = ?
        # (None, 2)
        # DELETE FROM users WHERE users.id = ?
        # (4,)
        user_id = fred.id
        self.session.delete(fred)
        self.session.commit()
        addresses = self.session.query(Address).filter(Address.user_id==user_id).all()
        self.assertEqual(len(addresses), 0, '用这种方式生成删除数据，将变更address中对应字段的user_id值，但不删除')
        addresses = self.session.query(Address).filter(Address.email_address=='fred@google.com').all()
        self.assertEqual(len(addresses), 1, '用这种方式生成删除数据，将变更address中对应字段的user_id值，但不删除')

        # 注意，如下代码在Mysql数据库中执行会报错
        # leo = User('leo', 'Leo Newton', 'XXXXXX')
        # leo.addresses = [Address(email_address='leo@google.com'), Address(email_address='leo@yahoo.com')]
        # self.session.add(leo)
        # self.session.commit()
        # user_id = leo.id
        # self.session.query(User).filter(User.name=='leo').delete()
        # addresses = self.session.query(Address).filter(Address.user_id==user_id).all()
        # self.assertEqual(len(addresses), 2, '用这种方式生成删除数据，不会变更address中对应字段的user_id值')

        wendy = User('wendy', 'Wendy Williams', 'foobar')
        mary = User('mary', 'Mary Contrary', 'xxg527')
        fred = User('fred', 'Fred Flinstone', 'blah')
        self.session.add_all([wendy, mary, fred ])
        self.session.commit()

        # 抛出这样的异常：sqlalchemy.exc.InvalidRequestError: Could not evaluate current criteria in Python.
        # self.session.query(User).filter(User.id.in_((1, 2, 3))).delete()
        # self.session.commit()
        # 正常执行
        # self.session.query(User).filter(or_(User.id == 1, User.id == 2, User.id == 3)).delete()
        # self.session.commit()

        # 搜了下找到《Sqlalchemy delete subquery》
        # http://stackoverflow.com/questions/7892618/sqlalchemy-delete-subquery
        # 这个问题，提到了 delete 的一个注意点：删除记录时，默认会尝试删除 session 中符合条件的对象，
        # 而 in 操作估计还不支持，于是就出错了。解决办法就是删除时不进行同步，然后再让 session 里的所有实体都过期：
        # 此外，update 操作也有同样的参数
        self.session.query(User).filter(User.id.in_((1, 2, 3))).delete(synchronize_session=False)
        self.session.commit()

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_modify(self):
        user = self.session.query(User).filter(User.name=='ed').first()
        self.assertTrue(len(self.session.dirty) == 0, '在修改前确保系统没有脏数据。')

        user.password = '1234567'
        self.assertTrue(len(self.session.dirty) == 1, '修改后确保系统已经存在了一条脏数据。')
        self.assertTrue(user in self.session.dirty)

        # UPDATE users SET password=? WHERE users.id = ?
        # ('1234567', 1)
        self.session.commit()
        other_user = self.session.query(User).filter(User.name=='ed').first()
        self.assertTrue(other_user.password == '1234567', '确保修改的数据已经正确写入。')
        self.assertTrue(len(self.session.dirty) == 0, '在修改提交后确保系统没有脏数据。')

        # 另外一种修改方法，这种方式直接生成Update SQL语句，不用先取出数据，也可以一次修改多个记录
        # UPDATE users SET password=? WHERE users.name = ?
        # ('password', 'ed')
        self.session.query(User).filter(User.name=='ed').update({User.password:"password"})
        self.assertTrue(len(self.session.dirty) == 0, '直接filter后跟update函数是没有产生脏数据的。')
        other_user = self.session.query(User).filter(User.name=='ed').first()
        self.assertTrue(other_user.password == 'password', '确保修改的数据已经正确写入。')

        # 替换一个已有主键的记录，在MySQL中生成INSERT … ON DUPLICATE KEY UPDATE
        user = User('test', 'test', '12345')
        user.id = 1
        self.session.merge(user)
        self.session.commit()
        user_num = self.session.query(User).filter(User.name=='ed').count()
        self.assertEqual(user_num, 0)


    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_rollback(self):
        fake_user = User('fakeuser', 'Invalid', '12345')
        self.session.add(fake_user)
        self.assertTrue(fake_user.id is None, '插入前没有ID。')
        self.session.flush()
        self.assertTrue(fake_user.id == 2, 'Flush写入数据库，得到ID。注意，此时并未提交。')

        users = self.session.query(User).filter(User.name.in_(['ed', 'fakeuser'])).all()
        self.assertTrue(len(users) == 2, '回滚前确保系统已经有两个用户数据。')
        self.assertTrue(fake_user in self.session, '回滚前确保里面包含新建用户。')
        self.assertTrue(fake_user in users, '回滚前确保里面包含新建用户。')

        self.session.rollback()
        self.assertTrue(fake_user not in self.session, '确保回滚之后，session中不包含新建用户。')
        users = self.session.query(User).filter(User.name.in_(['ed', 'fakeuser'])).all()
        self.assertTrue(len(users) == 1, '确保回滚之后，数据库中不包含新建用户。')
        self.assertTrue(fake_user not in self.session, '确保回滚后，数据库中不包含新建用户。')
        self.assertTrue(fake_user not in users, '确保回滚之后，数据库中不包含新建用户。')

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_bulk_insert(self):
        # 这种批量插入方式最快，不过要注意SQL语句最大长度设置
        from random import randint
        self.session.execute(
            User.__table__.insert(),
            [{'name': randint(1, 100),'password': randint(1, 100)} for i in xrange(10000)]
            )
        self.session.commit()
        user_num = self.session.query(User).count()
        self.assertEqual(user_num, 10001)

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_query(self):
        self.session.add_all([
            User('wendy', 'Wendy Williams', 'foobar'),
            User('mary', 'Mary Contrary', 'xxg527'),
            User('fred', 'Fred Flinstone', 'blah')
        ])

        # 按主键查询
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.id = ?
        # LIMIT ? OFFSET ?
        # (1, )
        user = self.session.query(User).get(1)
        self.assertTrue(id(user) == id(self.ed_user))      # 其实是同一个实例
        self.assertTrue(user.name == 'ed')
        self.assertTrue(user.fullname == 'Ed Jones')
        # todo 奇怪的问题，上面语句运行前并没有先将前面的INSERT先运行

        # 简单查询，使用filter_by
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name = ?
        # LIMIT ? OFFSET ?
        # ('ed', 1, 0)
        user = self.session.query(User).filter_by(name='ed').first()
        self.assertTrue(id(user) == id(self.ed_user))      # 其实是同一个实例
        self.assertTrue(user.name == 'ed')
        self.assertTrue(user.fullname == 'Ed Jones')

        # 简单查询，使用filter
        # SELECT users.name AS users_name, users.fullname AS users_fullname
        # FROM users
        # WHERE users.name = ?
        # LIMIT ? OFFSET ?
        # ('ed', 1, 0)
        name, fullname = self.session.query(User.name, User.fullname).filter(User.name=='ed').first()
        self.assertTrue(name == 'ed')
        self.assertTrue(fullname == 'Ed Jones')

        # 简单查询，不等于
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name != ?
        # ('ed',)
        users = self.session.query(User).filter(User.name!='ed').all()
        self.assertTrue(len(users) == 3)

        # 用for代替all
        for user in self.session.query(User).filter(User.name!='ed'):
            self.assertTrue(user.name == 'wendy' or user.name == 'mary' or user.name == 'fred')

        # 简单查询，like
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name LIKE ?
        # ('%ed%',)
        users = self.session.query(User).filter(User.name.like('%ed%')).all()
        self.assertTrue(len(users) == 2)

        # 简单查询，in
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name IN (?, ?, ?)
        # ('ed', 'wendy', 'jack')
        users = self.session.query(User).filter(User.name.in_(['ed', 'wendy', 'jack'])).all()
        self.assertTrue(len(users) == 2)

        # 简单查询，named tuple输出
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        users = self.session.query(User, User.name).all()
        self.assertTrue(len(users) == 4)
        self.assertTrue(users[0].User.name == 'ed')
        self.assertTrue(users[0].name == 'ed')
        self.assertTrue(type(users[0]).__name__ == 'NamedTuple')

        # 简单查询，切片转化成limit offset
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users ORDER BY users.id
        # LIMIT ? OFFSET ?
        # (2, 1)
        users = self.session.query(User).order_by(User.id)[1:3]     # LIMIT 2 OFFSET 1
        self.assertTrue(len(users) == 2)

        # 简单查询，直接使用limit offset
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users ORDER BY users.id
        # LIMIT ? OFFSET ?
        # (2, 1)
        users = self.session.query(User).order_by(User.id).limit(2).offset(1).all()     # LIMIT 2 OFFSET 1
        self.assertTrue(len(users) == 2)

        # 简单查询，not in
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name NOT IN (?, ?, ?)
        # ('ed', 'wendy', 'jack')
        users = self.session.query(User).filter(~User.name.in_(['ed', 'wendy', 'jack'])).all()
        self.assertTrue(len(users) == 2)

        # 简单查询，等于Null
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name IS NULL
        users = self.session.query(User).filter(User.name == None).all()
        self.assertTrue(len(users) == 0)

        # 简单查询，不等于Null
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name IS NOT NULL
        users = self.session.query(User).filter(User.name != None).all()
        self.assertTrue(len(users) == 4)

        # 简单查询，and
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name = ? AND users.fullname = ?
        # ('ed', 'Ed Jones')
        users = self.session.query(User).filter(and_(User.name == 'ed', User.fullname == 'Ed Jones')).all()
        self.assertTrue(len(users) == 1)

        # 简单查询，级联filter
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name = ? AND users.fullname = ?
        # ('ed', 'Ed Jones')
        users = self.session.query(User).filter(User.name == 'ed').filter(User.fullname == 'Ed Jones').all()
        self.assertTrue(len(users) == 1)

        # 简单查询，or
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name = ? OR users.name = ?
        # ('ed', 'wendy')
        users = self.session.query(User).filter(or_(User.name == 'ed', User.name == 'wendy')).all()
        self.assertTrue(len(users) == 2)

        # 简单查询，order by desc
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name LIKE ? ORDER BY users.id DESC
        # ('%ed',)
        users = self.session.query(User).filter(User.name.like('%ed')).order_by(User.id.desc()).all()
        self.assertTrue(len(users) == 2)
        self.assertTrue(users[0].name == 'fred')

        # 简单查询，order by
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name LIKE ? ORDER BY users.id
        # ('%ed',)
        users = self.session.query(User).filter(User.name.like('%ed')).order_by(User.id).all()
        self.assertTrue(len(users) == 2)
        self.assertTrue(users[0].name == 'ed')

        # one只能返回一行结果，否则抛出异常
        with self.assertRaises(MultipleResultsFound):
            self.session.query(User).one()

        # 没有数据时调用one，抛出异常
        with self.assertRaises(NoResultFound):
            self.session.query(User).filter(User.id == 99).one()

        # 直接传入条件字符串，非复杂情况不推荐
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE id<9 ORDER BY id
        users = self.session.query(User).filter("id<9").order_by("id").all()
        self.assertTrue(len(users) == 4)

        # 带参数的条件字符串，非复杂情况不推荐
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE id<? and name=? ORDER BY users.id
        # (9, 'fred')
        user = self.session.query(User).filter("id<:value and name=:name").params(value=9, name='fred').order_by(User.id).one()
        self.assertTrue(user.name == 'fred')

        # 直接使用select 语句
        # SELECT * FROM users where name=?
        # ('ed,)
        users = self.session.query(User).from_statement(
            "SELECT * FROM users where name=:name").params(name='ed').all()
        self.assertTrue(len(users) == 1)

        # 统计
        # SELECT count(*) AS count_1
        # FROM (SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name LIKE ?) AS anon_1
        # ('%ed',)
        user_num = self.session.query(User).filter(User.name.like('%ed')).count()
        self.assertTrue(user_num == 2)

        # 分组统计
        # SELECT count(users.name) AS count_1, users.name AS users_name
        # FROM users GROUP BY users.name
        user_nums = self.session.query(func.count(User.name), User.name).group_by(User.name).all()
        self.assertTrue((1, u'ed') in user_nums)
        self.assertTrue((1, u'fred') in user_nums)
        self.assertTrue((1, u'mary') in user_nums)
        self.assertTrue((1, u'wendy') in user_nums)

        # 排序
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name LIKE ? ORDER BY users.id
        # ('%ed',)
        users = self.session.query(User).filter(User.name.like('%ed')).order_by(User.id).all()
        self.assertTrue(len(users) == 2)
        self.assertEqual(users[0].name, 'ed')

        # 排序
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name LIKE ? ORDER BY users.id DESC
        # ('%ed',)
        users = self.session.query(User).filter(User.name.like('%ed')).order_by(User.id.desc()).all()
        self.assertTrue(len(users) == 2)
        self.assertEqual(users[0].name, 'fred')

        # 排序
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users
        # WHERE users.name LIKE ? ORDER BY users.name, users.id DESC
        # ('%ed',)
        users = self.session.query(User).filter(User.name.like('%ed')).order_by(User.name, User.id.desc()).all()
        self.assertTrue(len(users) == 2)
        self.assertEqual(users[0].name, 'ed')

        # 使用函数
        # SELECT sum(users.id) AS sum_1
        # FROM users
        user_id_sum = self.session.query(func.sum(User.id)).scalar()
        self.assertEqual(user_id_sum, 10)

        # sqlite 不支持md5函数
        # name_md5 = self.session.query(func.md5(User.name)).filter(User.id == 1).scalar()

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_relationship(self):
        jack = User('jack', 'Jack Bean', 'gjffdd')
        jack.addresses = [Address(email_address='jack@google.com'), Address(email_address='j25@yahoo.com')]
        self.assertTrue(jack.addresses[1].email_address == 'j25@yahoo.com')    # user中使用addresses引用Address
        self.assertTrue(jack.addresses[1].user.name == 'jack')    # address中使用user应用User

        self.session.add(jack)
        self.session.commit()

        user = self.session.query(User).filter_by(name='jack').one()
        self.assertTrue(user.addresses[1].email_address == 'j25@yahoo.com')
        self.assertTrue(user.addresses[1].user.name == 'jack')

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_join(self):
        jack = User('jack', 'Jack Bean', 'gjffdd')
        jack.addresses = [Address(email_address='jack@google.com'), Address(email_address='j25@yahoo.com')]
        self.session.add(jack)
        self.session.commit()

        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password, addresses.id AS addresses_id, addresses.email_address AS addresses_email_address, addresses.user_id AS addresses_user_id
        # FROM users, addresses
        # WHERE users.id = addresses.user_id AND addresses.email_address = ?
        # ('jack@google.com',)
        rows = self.session.query(User, Address)\
            .filter(User.id==Address.user_id)\
            .filter(Address.email_address=='jack@google.com')\
            .all()
        self.assertTrue(rows[0][0].name == 'jack')
        self.assertTrue(rows[0].User.name == 'jack')
        self.assertTrue(rows[0][1].email_address == 'jack@google.com')
        self.assertTrue(rows[0].Address.email_address == 'jack@google.com')
        self.assertTrue(type(rows[0]).__name__ == 'NamedTuple')

        # 因为有唯一的外键，系统知道用哪个条件去join
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users JOIN addresses ON users.id = addresses.user_id
        # WHERE addresses.email_address = ?
        # ('jack@google.com',)
        rows = self.session.query(User).join(Address).\
            filter(Address.email_address=='jack@google.com')\
            .all()
        self.assertTrue(rows[0].name == 'jack')

        # 指定了join条件
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users JOIN addresses ON users.id = addresses.user_id
        # WHERE addresses.email_address = ?
        # ('jack@google.com',)
        rows = self.session.query(User).join(Address, User.id==Address.user_id).\
            filter(Address.email_address=='jack@google.com')\
            .all()
        self.assertTrue(rows[0].name == 'jack')

        # left join, address 对应内容为空
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password
        # FROM users LEFT OUTER JOIN addresses ON users.id = addresses.user_id
        # WHERE users.name = ?
        rows = self.session.query(User).outerjoin(User.addresses) .\
            filter(User.name=='ed')\
            .all()
        self.assertTrue(rows[0].name == 'ed')

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_subquery(self):
        jack = User('jack', 'Jack Bean', 'gjffdd')
        jack.addresses = [Address(email_address='jack@google.com'), Address(email_address='j25@yahoo.com')]
        self.session.add(jack)
        self.session.commit()

        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password, anon_1.address_count AS anon_1_address_count
        # FROM users LEFT OUTER JOIN (SELECT addresses.user_id AS user_id, count(?) AS address_count
        # FROM addresses GROUP BY addresses.user_id) AS anon_1 ON users.id = anon_1.user_id ORDER BY users.id
        # ('*',)
        stmt = self.session.query(Address.user_id, func.count('*').label('address_count')).group_by(Address.user_id).subquery()
        rows = self.session.query(User, stmt.c.address_count).outerjoin((stmt, User.id==stmt.c.user_id)).order_by(User.id).all()
        self.assertTrue(len(rows) == 2)
        self.assertTrue(rows[0][0].name == 'ed')
        self.assertTrue(rows[0][1] == None)
        self.assertTrue(rows[1][0].name == 'jack')
        self.assertTrue(rows[1][1] == 2)

        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password, anon_1.id AS anon_1_id, anon_1.email_address AS anon_1_email_address, anon_1.user_id AS anon_1_user_id
        # FROM users JOIN (SELECT addresses.id AS id, addresses.email_address AS email_address, addresses.user_id AS user_id
        # FROM addresses
        # WHERE addresses.email_address != ?) AS anon_1 ON users.id = anon_1.user_id
        # ('j25@yahoo.com',)
        stmt = self.session.query(Address).filter(Address.email_address != 'j25@yahoo.com').subquery()
        adalias = aliased(Address, stmt)
        rows = self.session.query(User, adalias).join(adalias, User.addresses).all()
        self.assertTrue(len(rows) == 1)
        self.assertTrue(rows[0][0].name == 'jack')
        self.assertTrue(rows[0][1].email_address == 'jack@google.com')

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_exist(self):
        jack = User('jack', 'Jack Bean', 'gjffdd')
        jack.addresses = [Address(email_address='jack@google.com'), Address(email_address='j25@yahoo.com')]
        self.session.add(jack)
        self.session.commit()

        # SELECT users.name AS users_name
        # FROM users
        # WHERE EXISTS (SELECT *
        # FROM addresses
        # WHERE addresses.user_id = users.id)
        stmt = exists().where(Address.user_id==User.id)
        rows = self.session.query(User.name).filter(stmt).all()
        self.assertTrue(len(rows) == 1)
        self.assertTrue(type(rows[0]).__name__ == 'NamedTuple')
        self.assertTrue(rows[0][0] == 'jack')

        # SELECT users.name AS users_name
        # FROM users
        # WHERE EXISTS (SELECT 1
        # FROM addresses
        # WHERE users.id = addresses.user_id)
        rows = self.session.query(User.name).filter(User.addresses.any()).all()
        self.assertTrue(len(rows) == 1)
        self.assertTrue(rows[0][0] == 'jack')

        # SELECT users.name AS users_name
        # FROM users
        # WHERE EXISTS (SELECT 1
        # FROM addresses
        # WHERE users.id = addresses.user_id AND addresses.email_address LIKE ?)
        # ('%google%',)
        rows = self.session.query(User.name).filter(User.addresses.any(Address.email_address.like('%google%'))).all()
        self.assertTrue(len(rows) == 1)
        self.assertTrue(rows[0][0] == 'jack')

        # SELECT addresses.id AS addresses_id, addresses.email_address AS addresses_email_address, addresses.user_id AS addresses_user_id
        # FROM addresses
        # WHERE NOT (EXISTS (SELECT 1
        # FROM users
        # WHERE users.id = addresses.user_id AND users.name = ?))
        # ('jack',)
        rows = self.session.query(Address).filter(~Address.user.has(User.name=='jack')).all()
        self.assertTrue(len(rows) == 0)

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_eager_load(self):
        jack = User('jack', 'Jack Bean', 'gjffdd')
        jack.addresses = [Address(email_address='jack@google.com'), Address(email_address='j25@yahoo.com')]
        self.session.add(jack)
        self.session.commit()

        # 一次载入，而非延迟载入
        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password, addresses_1.id AS addresses_1_id, addresses_1.email_address AS addresses_1_email_address, addresses_1.user_id AS addresses_1_user_id
        # FROM users LEFT OUTER JOIN addresses AS addresses_1 ON users.id = addresses_1.user_id
        # WHERE users.name = ? ORDER BY addresses_1.id
        # ('jack',)
        user = self.session.query(User).options(joinedload('addresses')).filter_by(name='jack').one()
        self.assertTrue(user.name == 'jack')
        self.assertTrue(len(user.addresses) == 2)

        # SELECT users.id AS users_id, users.name AS users_name, users.fullname AS users_fullname, users.password AS users_password, addresses.id AS addresses_id, addresses.email_address AS addresses_email_address, addresses.user_id AS addresses_user_id
        # FROM addresses JOIN users ON users.id = addresses.user_id
        # WHERE users.name = ?
        # ('jack',)
        users = self.session.query(Address).join(Address.user).filter(User.name=='jack').options(contains_eager(Address.user)).all()
        self.assertTrue(users[0].email_address == 'jack@google.com')
        self.assertTrue(users[0].user.name == 'jack')
        self.assertTrue(users[1].email_address == 'j25@yahoo.com')



