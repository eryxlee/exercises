# -*- coding: utf-8 -*-
#
# SQLAlchemy几种数据库表关联映射的表述，主要案例来源于：
# http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html


from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    Table, desc)
from sqlalchemy.orm import (
    sessionmaker,
    relationship,
    backref,
)
from sqlalchemy.ext.declarative import declarative_base


# one to many example
def one2many():
    engine = create_engine('sqlite:///:memory:', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    Base = declarative_base()

    class Parent(Base):
        __tablename__ = 'parent'
        id = Column(Integer, primary_key=True)
        children = relationship("Child", backref="parent", order_by="Child.id")

    class Child(Base):
        __tablename__ = 'child'
        id = Column(Integer, primary_key=True)
        parent_id = Column(Integer, ForeignKey('parent.id'))

    Base.metadata.create_all(engine)
    parent = Parent(id=1)
    child1 = Child(id=1)
    child2 = Child(id=2)
    parent.children.append(child1)
    parent.children.append(child2)
    session.add(parent)
    session.commit()
    row = session.query(Parent).first()
    assert row.id == 1
    assert row.children[0].id == 1
    assert row.children[1].id == 2
    row = session.query(Child).filter(Child.id == 2).first()
    assert row.id == 2
    assert row.parent.id == 1
    Base.metadata.drop_all(engine)


# many to one example
def many2one():
    engine = create_engine('sqlite:///:memory:', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    Base = declarative_base()

    class Parent(Base):
        __tablename__ = 'parent'
        id = Column(Integer, primary_key=True)
        child_id = Column(Integer, ForeignKey('child.id'))
        child = relationship("Child", backref=backref("parents", order_by=desc(id)))

    class Child(Base):
        __tablename__ = 'child'
        id = Column(Integer, primary_key=True)

    Base.metadata.create_all(engine)
    child = Child(id=1)
    parent1 = Parent(id=1)
    parent2 = Parent(id=2)
    parent1.child = child
    parent2.child = child
    session.add(child)
    session.commit()
    row = session.query(Parent).filter(Parent.id == 2).first()
    assert row.id == 2
    assert row.child.id == 1
    row = session.query(Child).filter(Child.id == 1).first()
    assert row.id == 1
    assert row.parents[1].id == 1
    Base.metadata.drop_all(engine)


# one to one example
def one2one():
    engine = create_engine('sqlite:///:memory:', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    Base = declarative_base()

    class Parent(Base):
        __tablename__ = 'parent'
        id = Column(Integer, primary_key=True)
        child = relationship("Child", uselist=False, backref="parent")

    class Child(Base):
        __tablename__ = 'child'
        id = Column(Integer, primary_key=True)
        parent_id = Column(Integer, ForeignKey('parent.id'))

    Base.metadata.create_all(engine)
    parent = Parent(id=1)
    child = Child(id=1)
    parent.child = child
    session.add(parent)
    session.commit()
    row = session.query(Parent).filter(Parent.id == 1).first()
    assert row.id == 1
    assert row.child.id == 1
    row = session.query(Child).filter(Child.id == 1).first()
    assert row.id == 1
    assert row.parent.id == 1
    Base.metadata.drop_all(engine)


# many to many example
def many2many():
    engine = create_engine('sqlite:///:memory:', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    Base = declarative_base()
    association_table = Table('association', Base.metadata,
                              Column('left_id', Integer, ForeignKey('left.id')),
                              Column('right_id', Integer, ForeignKey('right.id'))
                              )

    class Left(Base):
        __tablename__ = 'left'
        id = Column(Integer, primary_key=True)
        rights = relationship("Right",
                              secondary=association_table,
                              order_by="desc(Right.id)",
                              backref=backref("lefts", order_by=desc(id)))

    class Right(Base):
        __tablename__ = 'right'
        id = Column(Integer, primary_key=True)

    Base.metadata.create_all(engine)
    left1 = Left(id=1)
    left2 = Left(id=2)
    left3 = Left(id=3)
    right1 = Right(id=1)
    right2 = Right(id=2)
    left1.rights.append(right1)
    left1.rights.append(right2)
    left2.rights.append(right1)
    left3.rights.append(right2)
    session.add(left1)
    session.add(left2)
    session.add(left3)
    session.add(right1)
    session.add(right2)
    session.commit()
    row = session.query(Left).filter(Left.id == 1).first()
    assert row.id == 1
    assert row.rights[0].id == 2
    assert row.rights[1].id == 1
    assert len(row.rights) == 2
    row = session.query(Left).filter(Left.id == 2).first()
    assert row.id == 2
    assert row.rights[0].id == 1
    assert len(row.rights) == 1
    row = session.query(Left).filter(Left.id == 3).first()
    assert row.id == 3
    assert row.rights[0].id == 2
    assert len(row.rights) == 1
    row = session.query(Right).filter(Right.id == 1).first()
    assert row.id == 1
    assert row.lefts[0].id == 2
    assert row.lefts[1].id == 1
    assert len(row.lefts) == 2
    row = session.query(Right).filter(Right.id == 2).first()
    assert row.id == 2
    assert row.lefts[0].id == 3
    assert row.lefts[1].id == 1
    assert len(row.lefts) == 2
    Base.metadata.drop_all(engine)


# many to many example with association table define behind
def many2many_lambda_asso():
    engine = create_engine('sqlite:///:memory:', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    Base = declarative_base()

    class Left(Base):
        __tablename__ = 'left'
        id = Column(Integer, primary_key=True)
        rights = relationship("Right",
                              secondary=lambda: association_table,
                              backref="lefts")

        def __init__(self, id):
            self.id = id

    class Right(Base):
        __tablename__ = 'right'
        id = Column(Integer, primary_key=True)

        def __init__(self, id):
            self.id = id

    association_table = Table('association', Base.metadata,
                              Column('left_id', Integer, ForeignKey('left.id')),
                              Column('right_id', Integer, ForeignKey('right.id'))
                              )
    Base.metadata.create_all(engine)
    Base.metadata.drop_all(engine)


# many to many example with association table define behind
def many2many_literal_asso():
    engine = create_engine('sqlite:///:memory:', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    Base = declarative_base()

    class Left(Base):
        __tablename__ = 'left'
        id = Column(Integer, primary_key=True)
        rights = relationship("Right",
                              secondary="association",
                              backref="lefts")

        def __init__(self, id):
            self.id = id

    class Right(Base):
        __tablename__ = 'right'
        id = Column(Integer, primary_key=True)

        def __init__(self, id):
            self.id = id

    association_table = Table('association', Base.metadata,
                              Column('left_id', Integer, ForeignKey('left.id')),
                              Column('right_id', Integer, ForeignKey('right.id'))
                              )
    Base.metadata.create_all(engine)
    Base.metadata.drop_all(engine)


# many to many example with extra field in association table
# 也就是一个一对多，再加一个多对一
def many2many_extra_asso():
    engine = create_engine('sqlite:///:memory:', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base = declarative_base()

    class Association(Base):
        __tablename__ = 'association'
        left_id = Column(Integer, ForeignKey('left.id'), primary_key=True)
        right_id = Column(Integer, ForeignKey('right.id'), primary_key=True)  #
        extra_data = Column(String(50))
        right = relationship("Right", backref="left_assocs")

    class Left(Base):
        __tablename__ = 'left'
        id = Column(Integer, primary_key=True)
        rights = relationship("Association", backref="left")

    class Right(Base):
        __tablename__ = 'right'
        id = Column(Integer, primary_key=True)

    Base.metadata.create_all(engine)

    # create parent, append a child via association
    p = Left(id=1)
    a = Association(extra_data="some data")
    a.right = Right(id=1)
    p.rights.append(a)
    # iterate through child objects via association, including association
    # attributes
    for assoc in p.rights:
        print assoc.extra_data
        print assoc.right.id
    Base.metadata.drop_all(engine)


if __name__ == "__main__":
    one2many()
    many2one()
    one2one()
    many2many()
    many2many_lambda_asso()
    many2many_literal_asso()
    many2many_extra_asso()
