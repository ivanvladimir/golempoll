#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Dashboard - polling system for golem
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
    make_response
    )
from flask.ext.login import login_required

# Extra import
from datetime import datetime
import uuid
from json import loads

# Local import
from database import db_session
from models import User, Experiment, ExperimentUser
from forms import ExperimentF, UserInviteF

# Registering Blueprint
dashboardB = Blueprint('dashboard', __name__,template_folder='templates')

# Managing dashboard
@dashboardB.route("/")
@login_required
def dashboard():
    return render_template('adminindex.html')

# Creating a new experiment
@dashboardB.route("/create/experiment", methods=['GET','POST'])
@login_required
def experiment_new():
    form=ExperimentF(request.form)
    if form.cancel.data:
        return redirect(url_for('dashboard'))
    if form.validate_on_submit():
        exp=Experiment()
        form.populate_obj(exp)
        db_session.add(exp)
        db_session.commit()
        return redirect('/dashboard/info/experiment/'+str(exp.id))
    else:
        return render_template('experiment_edit.html',form=form,type='create')

# Showing info
@dashboardB.route("/info/experiment/<int:expid>")
@login_required
def experiment_info(expid):
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido")
    return render_template('experiment_info.html',exp=exp)

# Showing info
@dashboardB.route("/result/<result>")
@login_required
def show_result(result):
    result=loads(result)
    proj_id = int(request.cookies.get('running_exp'))
    resp = make_response(render_template('result.html',result=result,expid=proj_id))
    resp.set_cookie('running_exp', "", expires=0)
    resp.set_cookie('running_user', "", expires=0)
    return resp



# Edit an experiment
@dashboardB.route("/edit/experiment/<int:expid>", methods=['GET','POST'])
@login_required
def experiment_edit(expid):
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido")
    form=ExperimentF()
    if form.cancel.data:
        return redirect(url_for('.dashboard'))
    if form.validate_on_submit():
        form.populate_obj(exp)
        exp.date_modification=datetime.now()
        db_session.add(exp)
        db_session.commit()
        return redirect(url_for('.experiment_info',expid=expid))
    form.name.data=exp.name
    form.definition.data=exp.definition
    form.invitation.data=exp.invitation
    form.instructions.data=exp.instructions
    form.description.data=exp.description

    return render_template('experiment_edit.html',
                form=form,type='edit',expid=expid)

# List experiments
@dashboardB.route("/list/experiment")
@login_required
def experiment_list():
    return render_template('experiments.html')

# Delete experiment
@dashboardB.route("/delete/experiment/<int:expid>")
@login_required
def experiment_delete(expid):
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido")
    db_session.delete(exp)
    db_session.commit()
    return redirect(url_for('.dashboard'))

# Select experiment for invite user 
@dashboardB.route("/select/experiment/<int:expid>")
@login_required
def experiment_select(expid):
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido")
    resp = make_response(render_template('adminindex.html'))
    resp.set_cookie('project', str(expid))
    resp.set_cookie('project_name', exp.name)
    return resp

# Close experiment
@dashboardB.route("/cerrar/experiment")
@login_required
def experiment_close():
    resp = make_response(render_template('adminindex.html'))
    resp.set_cookie('project', "",expires=0)
    resp.set_cookie('project_name', "",expires=0)
    return resp

# Clone experiment
@dashboardB.route("/clone/experiment/<int:expid>")
@login_required
def experiment_clone(expid):
    exp_=db_session.query(Experiment).get(expid)
    if not exp_:
        return render_template('error.html',message="Experimento no definido")
    exp=Experiment()
    exp.name=exp_.name
    exp.definition=exp_.definition
    exp.description=exp_.description
    exp.instructions=exp_.instructions
    exp.invitation=exp_.invitation
    db_session.add(exp)
    db_session.commit()
    return redirect(url_for('.experiment_info',expid=expid))

# Activate experiment
@dashboardB.route("/on/experiment/<int:expid>")
@login_required
def experiment_on(expid):
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido")
    exp.status=True 
    db_session.add(exp)
    db_session.commit()
    return redirect(url_for('.experiment_info',expid=expid))

@dashboardB.route("/off/experiment/<int:expid>")
@login_required
def experiment_offf(expid):
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido")
    exp.status=False 
    db_session.add(exp)
    db_session.commit()
    return redirect(url_for('.experiment_info',expid=expid))

# Testing experiment
@dashboardB.route("/test/experiment/<int:expid>")
@login_required
def experiment_test(expid):
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido")
    resp = make_response(render_template('poll_prev.html',
                        instructions=exp.instructions ))
    resp.set_cookie('running_exp',str(expid))
    resp.set_cookie('running_user',"",expires=0)
    return resp


# ------------------ Managing users -----------------------------------------
# Create user
@dashboardB.route("/create/user")
@login_required
def user_new():
    u=uuid.uuid4()
    userid=str(u)
    user=User(userid)
    db_session.add(user)
    db_session.commit()
    return render_template('user_created.html',userid=userid)

# Invite user
@dashboardB.route("/invite/user", methods=['GET','POST'])
@login_required
def user_invite():
    """Invite a user via email"""
    project = request.cookies.get('project')
    if not project:
        return render_template('error.html',message="Projecto no seleccionado")
    form=UserInviteF(request.form)
    if form.cancel.data:
        return redirect(url_for(dashboard))
    if form.validate_on_submit():
        u=uuid.uuid4()
        userid=str(u)
        user=User(userid)
        db_session.add(user)
        db_session.commit()
        return redirect(url_for('user_info',userid=userid))
    else:
        return render_template('email_edit.html',form=form)

@dashboardB.route("/invite/user/<userid>")
@login_required
def user_invite_userid(userid):
    """Invite a user via email"""
    proj = request.cookies.get('project')
    if not proj:
        return render_template('error.html',message="Projecto no seleccionado")
    try:
        user=User.query.filter(User.userid==userid).one()
    except:
        return render_template('error.html',message="Usuario in existente")
    if not user.confirmed:
        return render_template('error.html',message="Usuario no ha confirmado")
    if not user.accepted:
        return render_template('error.html',message="Usuario no activo")
    exp=Experiment.query.ge(int(proj))
    try:
        db_session.query(User.id,User.experiments).filter(User.id==userid).one()
    except:
        eu=ExperimentUser(experiment=exp,user=user,accepted=False,finish=False,date_invited=datetime.now())
        db_session.add(eu)
        db_session.commit()    
        # TODO: Send EMAIL
        #msg= Message(proj.invitation.format(
        #    URL="/confirm/"+userid,
        #    URL_DEL="/delete/user/"+userid),
        #)
        return redirect(url_for('.user_info',userid=user.userid))
    return render_template('error.html',message="Usuario ya activo en ese experimento")

# List users
@dashboardB.route("/list/user")
def user_list():
    return render_template('users.html')

# Show info from user
@dashboardB.route("/info/user/<userid>")
@login_required
def user_info(userid):
    user=User.query.filter(User.userid==userid).one()
    if not user:
        return render_template('error.html',message="Usuario existente")
    return render_template('user_info.html',user=user)




@dashboardB.route("/invite")
@login_required
def experiment_invite():
    return redirect(url_for('dashboard'))

