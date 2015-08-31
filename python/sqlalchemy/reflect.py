# -*- coding: utf-8 -*-

from sqlalchemy import (
    create_engine,
    event,
    Table,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, DeferredReflection

# 因类定义在前，无法传入engine参数，需要使用DeferredReflection机制
Base = declarative_base(cls=DeferredReflection)


# 利用反射机制根据现有数据库表定义User 类，这时类属性均与字段名一样
class User(Base):
    __tablename__ = 'user'


# 将每个字段的名字加上一个前缀作为类的属性名
@event.listens_for(Table, "column_reflect")
def column_reflect(inspector, table, column_info):
    if table.metadata is Base.metadata:
        # set column.key = "attr_<lower_case_name>"
        column_info['key'] = "attr_%s" % column_info['name'].lower()


if __name__ == "__main__":
    engine = create_engine('mysql://root:@127.0.0.1:3306/test?charset=utf8', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # prepare调用时才使用反射机制
    Base.prepare(engine)

    ed_user = User()
    ed_user.attr_first_name = 'Ed'
    ed_user.attr_last_name = 'Jones'
    ed_user.attr_password = 'password'
    ed_user.attr_from = 'usa'

    session.add(ed_user)
    session.commit()

    stmt = session.query(User.attr_id, User.attr_first_name, User.attr_from) \
        .filter(User.attr_first_name == 'Ed')
    tuple_rows = stmt.all()

    # 删除两个表中的数据
    session.query(User).delete()
    session.commit()

