#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# User interface for polling system
# ----------------------------------------------------------------------
# ivan vladimir meza-ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2013/iimas/unam
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

from yaml import load, dump
from flask.ext.login import make_secure_token

secret_key="change this for deployment"

class User:
    def __init__(self,userid=None,data={}):
        self.userid=userid
        self.data=data

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.userid

    def get_auth_token(self):
        return make_secure_token(self.userid, key=secret_key)

