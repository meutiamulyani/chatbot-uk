from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from provider.db import Base
from sqlalchemy.orm import relationship

class user_activity(Base):
    __tablename__ = 'user_activity'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    no_hp = Column(String, unique=True)
    activity = Column(String)

    find_job = relationship('find_job', back_populates='user_activity')

class find_job(Base):
    __tablename__ = 'find_job'

    id_find_job = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_user_activity = Column(Integer, ForeignKey('user_activity.id'))
    user_activity = relationship('user_activity', back_populates='find_job')
    
#     # data diri
    name = Column(String)
    role = Column(String)
    location = Column(String)
    email = Column(String)