#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Initialization of database for polling system for golem
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2014/iimas/unam
# ----------------------------------------------------------------------
# initdb.py is free software: you can redistribute it and/or modify
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

from database import init_db, db_session
from models import Admin

try:
    adms=Admin.query.all()
    if len(adms)>0:
        print "Your database is not empty..."
        for adm in adms:
            print ">>", adm
        print
except:
    init_db()

name='__'
while len(name)>0:
    name=raw_input('Id for new admin      : ')
    if len(name)==0:
        continue
    pwd =raw_input('Password for new admin: ')
    u=Admin(name,pwd)
    db_session.add(u)
    db_session.commit()


print "This is the information you added"
adms=Admin.query.all()
for adm in adms:
    print ">>", adm
