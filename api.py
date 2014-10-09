#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# extra api - polling system for golem
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


# Flask imports
from flask import (
    Blueprint,
    jsonify,
    request
    )
from flask.ext.login import login_required
from yaml import load

# Local import
from database import db_session
from models import ExperimentUser, Experiment

# Registering Blueprint
apiB = Blueprint('api', __name__,template_folder='templates')

# Managing dashboard
@apiB.route("/definition/<int:expid>")
@login_required
def definition(expid):
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return jsonify('No register')
    definition=load(exp.definition)
    return jsonify(definition)
 
@apiB.route("/definition/<int:expid>/<int:userid>",methods=['PUT'])
@login_required
def answer(expid,userid):
    exp=db_session.query(ExperimentUser).get((expid,userid))
    if not exp:
        return jsonify('No register')
    exp.janswers=request.ars.get('answers','[]')
    db_session.add(exp)
    db_session.commit()
    return jsonify(definition)
 