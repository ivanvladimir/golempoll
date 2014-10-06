#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Models for polling system for golem
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2014/iimas/unam
# ----------------------------------------------------------------------
# homepage.py is free software: you can redistribute it and/or modify
#    it under the terms of the gnu general public license as published by
#    the free software foundation, either version 3 of the license, or
#    (at your option) any later version.
#
#    this program is distributed in the hope that it will be useful,
#    but without any warranty; without even the implied warranty of
#    merchantability or fitness for a particular purpose.  see the
#    gnu general public license for more details.
#
#    you should have received a copy of the gnu general public license
#    along with this program.  if not, see <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------------

from sqlalchemy import relationship,Column, Integer, String, Boolean, Enum,DateTime, Table, ForeignKey
from flask.ext.login import make_secure_token
from flask.ext.bcrypt import Bcrypt
from database import Base

from datetime import datetime

bcrypt=Bcrypt()

secret_key="change this for deployment"

class Admin(Base):
    __tablename__ = 'admin'
    id            = Column(Integer, primary_key=True)
    name          = Column(String(50), unique=True,nullable=False)
    _passwd       = Column(String(120), unique=True,nullable=False)
    authenticated = Column(Boolean, default=False)

    def __init__(self, name=None, passwd=None):
        self.name    = name
        self._passwd = bcrypt.generate_password_hash(passwd)
    def check_passwd(self, passwd):
        return bcrypt.check_password_hash(self._passwd, passwd)
    def get_auth_token(self):
        return make_secure_token(self.id, unicode(self._passwd))
    def is_authenticated(self):
        return self.authenticated
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return unicode(self.name)

class User(Base):
    __tablename__ = 'users'
    id            = Column(Integer, primary_key = True)
    userid        = Column(String(64), nullable = False)
    email         = Column(String(120))
    authenticated = Column(Boolean, default=False)
    confirmed     = Column(Boolean, default=False)
    accepted      = Column(Boolean, default=False)
    year_birthday = Column(Integer, default=1990)
    level         = Column(Enum('prim', 'sec','prep','uni','pos'))
    previous      = Column(Enum('yes', 'no'))
    gender        = Column(Enum('M', 'F'))
    experiments   = relationship('ExperimentUser', backref='experimentee', lazy='dynamic')

    def __init__(self, userid):
        self.userid  = userid
    def get_auth_token(self):
        return make_secure_token(self.id, secret_key)
    def is_authenticated(self):
        return self.authenticated
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return unicode(self.userid)


class Experiment(Base):
    __tablename__ = 'experiments'
    id            = Column(Integer, primary_key = True)
    name          = Column(String(120),nullable=False)
    definition    = Column(String,nullable=False)
    description   = Column(String,nullable=False)
    date_creation = Column(DateTime,nullable=False)
    date_modification = Column(DateTime,nullable=False)
    instructions  = Column(String,nullable=False)
    invitation    = Column(String,nullable=False)
    status        = Column(Boolean,default=True)
    users         = relationship('ExperimentUser', backref='experiment', lazy='dynamic')
    
    def __init__(self):
        self.date_creation=datetime.now()
        self.date_modification=datetime.now()


experiment_user =  Table('experiment_user',
    Column('id_user',Integer,ForeignKey('users.id')),
    Column('id_experiment',Integer,ForeignKey('experiments.id')),
    Column('accepted',Boolean, default=False),
    Column('finish',Boolean, default=False),
    Column('date_invited',DateTime, default=0))
