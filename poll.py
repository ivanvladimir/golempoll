#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# polling system for golem
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
    redirect,
    url_for,
    render_template,
    request,
    make_response,
    current_app
    )
from flask.ext.login import (
    login_user,
    current_user,
    login_required)
import uuid
# Local Imports
from database import db_session
from models import User, Experiment, ExperimentUser
from forms import UserF, UserInviteF
# Registering Blueprint
pollB = Blueprint('poll', __name__,template_folder='templates')

# Managing poll y página principal
@pollB.route("/confirm/<userid>", methods=['GET','POST'])
@login_required
def user_confirmation(userid):
    user=User.query.filter(User.userid==userid).one()
    if not user:
            return render_template('error_poll.html',message="Usuario existente")
    if user.confirmed:
        return redirect(url_for('.login',userid=userid))
    form=UserF()
    if form.cancel.data:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        form.populate_obj(user)
        user.confirmed=True
        user.accepted=True
        db_session.add(user)
        db_session.commit()
        return redirect(url_for('.login',userid=userid))
    else:
        return render_template('user_info_edit.html',form=form,userid=userid)

# Managing experiments
@pollB.route("/<userid>")
def login(userid):
    user=User.query.filter(User.userid==userid)
    if not user:
        return render_template('error_poll.html',message="Usuario inexistente")
    try:
        user=user[0]
    except IndexError:
        return render_template('error_poll.html',message="Usuario inexistente")
    user.authenticated = True
    db_session.add(user)
    db_session.commit()
    login_user(user)
    if not user.confirmed:
        return redirect(url_for('.user_confirmation',userid=userid))
    return render_template('myexperiments.html',projs=user.experiments)
              
# Instrutions
@pollB.route("/poll/<int:expid>")
@login_required
def poll_(expid):
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error_poll.html',message="Experimento no definido")
    userid=current_user.get_id()
    user=User.query.filter(User.userid==userid).one()
    ans=db_session.query(ExperimentUser).get((user.id,expid))
    ans.accepted=True
    db_session.add(ans)
    db_session.commit()
    resp = make_response(render_template('poll_prev.html',
                        instructions=exp.instructions ))
    resp.set_cookie('running_exp', str(expid))
    resp.set_cookie('running_user', str(user.id))
    return resp

@pollB.route("/del/<int:expid>")
@login_required
def delete(expid):
    userid=current_user.get_id()
    user=User.query.filter(User.userid==userid).one()
    ans=db_session.query(ExperimentUser).get((user.id,expid))
    ans.finished=True
    ans.accepted=False
    db_session.add(ans)
    db_session.commit()
    return redirect(url_for('.index'))

@pollB.route("/self",methods=["POST"])
def self():
    email= request.form['email']
    user_mail=User.query.filter(User.email==email).all()
    if not user_mail:
        u=uuid.uuid4()
        userid=str(u)
        user=User(userid)
        user.email=email
        user.accepted=True
        db_session.add(user)
        db_session.commit()
    else:
        return render_template('error_poll.html',
            message="Usuario existente go to: "+current_app.config['BASE_NAME']+"/"+user_mail[0].userid)
    return redirect(url_for('.index'))


# Polling interface
@pollB.route("/poll")
@login_required
def poll():
    return render_template('poll.html'),

@pollB.route("/finish")
@login_required
def finish_poll():
    try:
        current_user.name
        resp = make_response(redirect(url_for('dashboard.dashboard')))
    except:
        proj_id = int(request.cookies.get('running_exp'))
        user_id = request.cookies.get('running_user')
        user=User.query.get(int(user_id))
        ans=db_session.query(ExperimentUser).get((user.id,proj_id))
        ans.finish=True
        db_session.add(ans)
        db_session.commit()
        resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('running_exp', "", expires=0)
    resp.set_cookie('running_user', "", expires=0)
    return resp


# Entry point for potential users
@pollB.route("/",methods=['GET','POST'])
def index():
    ''' Entrada principal para cuando no hay nadie '''
    if not current_user.is_authenticated():
        form=UserInviteF(request.form)
        if form.validate_on_submit():
            u=uuid.uuid4()
            userid=str(u)
            user=User(userid)
            form.populate_obj(user)
            db_session.add(user)
            db_session.commit()
            return redirect(url_for('index'))
        else:
            return render_template('index.html',form=form, active=True)
    else:
        return render_template('myexperiments.html')




