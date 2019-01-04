import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL

from bot.conf.cfg import getConfig

Base = declarative_base()

class Status(Base):
    __tablename__ = 'status'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    userid = Column(BigInteger)
    json = Column(JSONB)
    datetime = Column(DateTime)

    def __repr__(self):
        return "<Status(id = %s, userid = %s, json = %s, datetime = %s)>" % (self.id, self.userid, self.json, str(self.datetime))

'''
class Screenname(Base):
    __tablename__ = 'screenname'

    id = Column(Integer, primary_key=True)
    userid = Column(BigInteger)
    username = Column(String)
    utctimestamp = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<Status(id = %d," \
               " user_id = %d," \
               " user_name = %s,"\
               " timestamp = %s)>" % (self.id, self.userid, str(self.username), str(self.utctimestamp))

class Reply(Base):
    __tablename__ = 'reply'

    id = Column(Integer, primary_key=True)
    statusid = Column(BigInteger)
    replycount = Column(Integer)
    utctimestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return "<Status(id = %d," \
               " status_id = %d," \
               " reply_count = %d,"\
               " timestamp = %s)>" % (self.id, self.statusid, self.replycount, str(self.utctimestamp))

class Favorite(Base):
    __tablename__ = 'favorite'

    id = Column(Integer, primary_key=True)
    statusid = Column(BigInteger)
    favoritecount = Column(Integer)
    utctimestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return "<Status(id = %d," \
               " status_id = %d," \
               " favorite_count = %d,"\
               " timestamp = %s)>" % (self.id, self.statusid, self.favoritecount, str(self.utctimestamp))

class Retweet(Base):
    __tablename__ = 'retweet'

    id = Column(Integer, primary_key=True)
    statusid = Column(BigInteger)
    retweetcount = Column(Integer)
    utctimestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return "<Status(id = %d," \
               " satus_id = %d," \
               " retweet_count = %d,"\
               " timestamp = %s)>" % (self.id, self.statusid, self.retweetcount, str(self.utctimestamp))
'''

config = getConfig()
url = URL("postgresql",
          username=config['postgresql']['username'],
          password=config['postgresql']['password'],
          host=config['postgresql']['host'],
          port=config['postgresql']['port'],
          database=config['postgresql']['database'],
          query=None)
engine = create_engine(url, client_encoding='utf8', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()