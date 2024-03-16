import datetime
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    DateTime, 
    JSON, 
    Boolean, 
    Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr, relationship
from typing import Dict
from sqlalchemy import ForeignKey
from sqlalchemy import Enum

Base = declarative_base()


class TimestampMixin(object):
    """
    Mixin for adding created_at and updated_at columns to models
    """
    @declared_attr
    def created_at(self):
        """
        Created at column
        """
        return Column(DateTime, default=datetime.datetime.utcnow)

    @declared_attr
    def updated_at(self):
        """
        Updated at column
        """
        return Column(
            DateTime, 
            default=datetime.datetime.utcnow, 
            onupdate=datetime.datetime.utcnow
        )
    

class User(Base, TimestampMixin):
    """
    User model
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)


class Messages(Base, TimestampMixin):
    """
    Messages model
    """
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    messages = Column(JSON, nullable=False)
    user = relationship('User', backref='messages')



