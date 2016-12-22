from sqlalchemy import (
    Column,
    Index,
    Integer,
    Unicode,
    DateTime,
)

from .meta import Base
import datetime


class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    body = Column(Unicode)
    creation_date = Column(DateTime, default=datetime.datetime.utcnow)

Index('my_index', Entry.title, unique=True, mysql_length=255)
