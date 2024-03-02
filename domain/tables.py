from sqlalchemy import Column, Integer, String, Float,ForeignKey,DateTime,Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class UserTable(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String)
    username = Column(String)
    hash = Column(String)
    realname = Column(String)
    description = Column(String)

class PostTable(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, ForeignKey('user.username', ondelete='CASCADE'))
    title = Column(String(50))
    content = Column(String(200))
    category = Column(String(30))
    date = Column(DateTime, default=datetime.now)
    no_likes = Column(Integer,default=0)
    user = relationship('UserTable')

class LikesTable(Base):
    __tablename__ = 'likes'
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    post_id = Column(Integer, ForeignKey('post.id', ondelete='CASCADE'), primary_key=True)


class CommentTable(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('post.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    content = Column(String)
    created_at = Column(DateTime, default=datetime.now)


class GroupTable(Base):
    __tablename__ = 'groups'

    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String)
    description = Column(String)
    creation_date = Column(DateTime, default=datetime.now)
    number_of_members = Column(Integer)
    permission = Column(Boolean)
    creator_id = Column(Integer)


class MembersTable(Base):

    __tablename__='members'
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True)

