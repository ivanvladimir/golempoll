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
    make_response, 
    current_app
    )
from flask.ext.login import login_required

# Extra import
from datetime import datetime
import uuid
from json import loads, dumps

# Local import
from database import db_session, recent
from models import User, Experiment, ExperimentUser
from forms import ExperimentF, UserInviteF
from flask.ext.mail import Message
from mail import mail

# Registering Blueprint
dashboardB = Blueprint('dashboard', __name__,template_folder='templates')

def add_users(proj,ids):
    exp=Experiment.query.get(int(proj))
    for idd in ids:
        user=User.query.get(idd)
        #msg= Message(proj.invitation.format(
        #    URL="/confirm/"+user.userid,
        #    URL_DEL="/delete/user/"+user.userid))
        eu=ExperimentUser(experiment=exp,user=user,accepted=False,finish=False,date_invited=datetime.now())
        db_session.add(eu)
        db_session.commit()
       
# Managing dashboard
@dashboardB.route("/")
@login_required
def dashboard():
    expid = request.cookies.get('project')
    if expid:
        exp=db_session.query(Experiment).get(expid)
    else:
        exp=None
    return render_template('adminindex.html',exp=exp,recent=recent.get())

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
        return redirect(url_for('.experiment_info',expid=exp.id))
    else:
        return render_template('experiment_edit.html',form=form,type='create',recent=recent.get())

# Showing info
@dashboardB.route("/info/experiment")
@dashboardB.route("/info/experiment/<int:expid>")
@login_required
def experiment_info(expid=None):
    if not expid:
        expid = request.cookies.get('project')
        if not expid:
            return render_template('error.html',message="Proyecto no seleccionado",recent=recent.get())
        expid=int(expid)
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido",recent=recent.get())
    return render_template('experiment_info.html',exp=exp,recent=recent.get())

# Showing live info
@dashboardB.route("/live/experiment")
@dashboardB.route("/live/experiment/<int:expid>")
@login_required
def experiment_live(expid=None):
    if not expid:
        expid = request.cookies.get('project')
        if not expid:
            return render_template('error.html',message="Proyecto no seleccionado",recent=recent.get())
        expid=int(expid)
    exp=db_session.query(Experiment).get(expid)
    filename=exp.name+".csv"
    keepcharacters = (' ','.','_')
    filename=    "".join(c for c in filename if c.isalnum() or c in
        keepcharacters).rstrip()
    if not exp:
        return render_template('error.html',message="Experimento no definido",recent=recent.get())
    return render_template('experiment_live.html',exp=exp,recent=recent.get(),fs=filename)



# Showing info
@dashboardB.route("/result/<result>")
@login_required
def show_result(result):
    result=loads(result)
    proj_id = request.cookies.get('running_exp')
    resp = make_response(render_template('result.html',result=result,expid=int(proj_id)))
    resp.set_cookie('running_exp', "", expires=0)
    resp.set_cookie('running_user', "", expires=0)
    return resp



# Edit an experiment
@dashboardB.route("/edit/experiment/<int:expid>", methods=['GET','POST'])
@login_required
def experiment_edit(expid):
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido",recent=recent.get())
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
    form.reinvitation.data=exp.reinvitation
    form.instructions.data=exp.instructions
    form.description.data=exp.description

    return render_template('experiment_edit.html',
                form=form,type='edit',expid=expid,recent=recent.get())

# List experiments
@dashboardB.route("/list/experiment")
@login_required
def experiment_list():
    return render_template('experiments.html',recent=recent.get())

# Delete experiment
@dashboardB.route("/delete/experiment")
@dashboardB.route("/delete/experiment/<int:expid>")
@login_required
def experiment_delete(expid=None):
    if not expid:
        expid = request.cookies.get('project')
        if not expid:
            return render_template('error.html',message="Proyecto no seleccionado",recent=recent.get())
        return render_template('error.html',message="Proyecto no seleccionado",recent=recent.get())
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido",recent=recent.get())
    db_session.delete(exp)
    db_session.commit()
    return redirect(url_for('.dashboard'))

# Select experiment for invite user 
@dashboardB.route("/select/experiment")
@dashboardB.route("/select/experiment/<int:expid>")
@login_required
def experiment_select(expid):
    if not expid:
        expid = request.cookies.get('project')
        if not expid:
            return render_template('error.html',message="Proyecto no seleccionado",recent=recent.get())
        return render_template('error.html',message="Proyecto no seleccionado",recent=recent.get())
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido",recent=recent.get())
    resp = make_response(redirect(url_for('.dashboard')))
    resp.set_cookie('project', str(expid))
    resp.set_cookie('project_name', exp.name)
    recent.pull(expid)
    return resp

# Close experiment
@dashboardB.route("/close/experiment")
@login_required
def experiment_close():
    resp = make_response(redirect(url_for('.dashboard')))
    expid = request.cookies.get('project')
    name = request.cookies.get('project_name')
    recent.push(int(expid),name)
    resp.set_cookie('project', "",expires=0)
    resp.set_cookie('project_name', "",expires=0)

    return resp

# Clone experiment
@dashboardB.route("/clone/experiment")
@dashboardB.route("/clone/experiment/<int:expid>")
@login_required
def experiment_clone(expid=None):
    if not expid:
        expid = request.cookies.get('project')
        if not expid:
            return render_template('error.html',message="Proyecto no seleccionado",recent=recent.get())
        expid=int(expid)
    exp_=db_session.query(Experiment).get(expid)
    if not exp_:
        return render_template('error.html',message="Experimento no definido",recent=recent.get())
    exp=Experiment()
    exp.name="CLONE:"+exp_.name
    exp.definition=exp_.definition
    exp.description=exp_.description
    exp.instructions=exp_.instructions
    exp.invitation=exp_.invitation
    exp.reinvitation=exp_.reinvitation
    db_session.add(exp)
    db_session.commit()
    return redirect(url_for('.experiment_info',expid=expid))

# Activate experiment
@dashboardB.route("/on/experiment/<int:expid>")
@login_required
def experiment_on(expid):
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido",recent=recent.get())
    exp.status=True 
    db_session.add(exp)
    db_session.commit()
    return redirect(url_for('.experiment_info',expid=expid))

@dashboardB.route("/off/experiment/<int:expid>")
@login_required
def experiment_off(expid):
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido",recent=recent.get())
    exp.status=False 
    db_session.add(exp)
    db_session.commit()
    return redirect(url_for('.experiment_info',expid=expid))

# Testing experiment
@dashboardB.route("/test/experiment")
@dashboardB.route("/test/experiment/<int:expid>")
@login_required
def experiment_test(expid=None):
    if not expid:
        expid = request.cookies.get('project')
        if not expid:
            return render_template('error.html',message="Proyecto no seleccionado",recent=recent.get())
        expid=int(expid)
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido",recent=recent.get())
    resp = make_response(render_template('poll_prev.html',
                        instructions=exp.instructions ))
    resp.set_cookie('running_exp',str(expid))
    resp.set_cookie('running_user',"",expires=0)
    return resp


# ------------------ Managing users -----------------------------------------
# Create user
@dashboardB.route("/create/user", methods=['GET','POST'])
@login_required
def user_new():
    """Create a user email"""
    form=UserInviteF(request.form)
    if form.cancel.data:
        return redirect(url_for(dashboard))
    if form.validate_on_submit():
        user_mail=User.query.filter(User.email==form.email.data).all()
        if not user_mail:
            u=uuid.uuid4()
            userid=str(u)
            user=User(userid)
            user.email=form.email.data
            user.accepted=True
            db_session.add(user)
            db_session.commit()
            return render_template('user_created.html',
                    userid=userid,
                    servername=current_app.config['BASE_NAME'],
                    recent=recent.get())
        else:
            return render_template('error.html',message="Usuario ["+form.email.data+"] ya definido con id:"+user_mail[0].userid,recent=recent.get())
    else:
        return render_template('email_edit.html',form=form,recent=recent.get(),opt="crear")

# Invite new user
@dashboardB.route("/invite/user", methods=['GET','POST'])
@login_required
def user_invite():
    """Invite a user via email"""
    project = request.cookies.get('project')
    if not project:
        return render_template('error.html',message="Proyecto no seleccionado",recent=recent.get())
    form=UserInviteF(request.form)
    if form.cancel.data:
        return redirect(url_for('.dashboard'))
    if form.validate_on_submit():
        user_mail=User.query.filter(User.email==form.email.data).all()
        if not user_mail:
            u=uuid.uuid4()
            userid=str(u)
            user=User(userid)
            user.accepted=True
            form.populate_obj(user)
            db_session.add(user)
            db_session.commit()
            return redirect(url_for('.user_info',userid=userid))
        else:
            return render_template('error.html',message="Usuario ["+form.email.data+"] ya definido con id:"+user_mail[0].userid,recent=recent.get())
    else:
        return render_template('email_edit.html',form=form,recent=recent.get())


# Invite several users
@dashboardB.route("/invite/users", methods=['POST'])
@login_required
def users_invite():
    """Invite a user via email"""
    project_name = request.cookies.get('project_name')
    if not project_name:
        return render_template('error.html',message="Proyecto no seleccionado",recent=recent.get())
    ids= request.form.keys()
    users=User.query.filter(User.id.in_(ids)).all()
    ids=dumps(ids)
    return  render_template('confirm_invitation.html',users=users,
        ids=ids,projname=project_name)

@dashboardB.route("/add/users")
@login_required
def users_add():
    """Invite a user via email"""
    project = request.cookies.get('project')
    if not project:
        return render_template('error.html',message="Proyecto no seleccionado",recent=recent.get())
    ids=loads(request.args.get('ids'))
    add_users(project,ids)
    return redirect(url_for(".experiment_info",expid=project)) 

# TODO properly
@dashboardB.route("/invite/nousers/<int:expid>")
@login_required
def experiment_nousers(expid):
    """Invite a user via email"""
    exp=db_session.query(Experiment).get(expid)
    if not exp:
        return render_template('error.html',message="Experimento no definido",recent=recent.get())
    return  render_template('nousers.html',projname=exp.name)

@dashboardB.route("/delete/user")
@dashboardB.route("/delete/user/<int:userid>")
@login_required
def user_delete(userid=None):
    if not userid:
        return render_template('error.html',message="Usuario no seleccionado",recent=recent.get())
    user=db_session.query(User).get(userid)
    if not user:
        return render_template('error.html',message="Usuario no encontrado",recent=recent.get())
    user.accepted=False
    db_session.add(user)
    db_session.commit()
    return redirect(url_for('.dashboard'))


@dashboardB.route("/nuke/user/<userid>")
@login_required
def user_nuke(userid):
    user=User.query.filter(User.userid==userid).one()
    if not user:
        return render_template('error.html',message="Usuario no encontrado",recent=recent.get())
    db_session.delete(user)
    db_session.commit()
    return redirect(url_for('.dashboard'))


@dashboardB.route("/invite/user/<int:userid>")
@login_required
def user_invite_userid(userid=None):
    """Invite a user via email"""
    proj = request.cookies.get('project')
    if not proj:
        return render_template('error.html',message="Proyecto no seleccionado",recent=recent.get())
    try:
        user=User.query.get(userid)
    except:
        return render_template('error.html',message="Usuario in existente",recent=recent.get())
    proj = int(proj)
    if not user.accepted:
        return render_template('error.html',message="Usuario no activo",recent=recent.get())
    exps=[0 for exp in user.experiments if exp.id==proj]
    if len(exps)==0:
        add_users(proj,[user.id])
        return redirect(url_for('.user_info',userid=user.userid))
    return render_template('error.html',message="Usuario ya activo en ese experimento",recent=recent.get())

@dashboardB.route("/reinvite")
@dashboardB.route("/reinvite/<userid>")
@dashboardB.route("/reinvite/<userid>/<int:expid>")
@login_required
def user_reinvite(userid=None,expid=None):
    """Invite a user via email"""
    try:
        user=User.query.filter(User.userid==userid).one()
    except:
        return render_template('error.html',message="Usuario in existente",recent=recent.get())
    if not user.accepted:
        return render_template('error.html',message="Usuario no activo",recent=recent.get())
    exps=[0 for exp in user.experiments if exp.id==expid]
    if len(exps)>0:
        ans=db_session.query(ExperimentUser).get((user.id,expid))
        if ans.accepted:
            #msg= Message(proj.invitation.format(
            #    URL="/confirm/"+user.userid,
            #    URL_DEL="/delete/user/"+user.userid))
            return redirect(url_for('.user_info',userid=user.userid))
        else:
            return render_template('error.html',message=u"Usuario declino",recent=recent.get())
    else:
        return render_template('error.html',message=u"Usuario no está activo en  experimento",recent=recent.get())


# List users
@dashboardB.route("/list/user")
@login_required
def user_list():
    """Invite a user via email"""
    proj = request.cookies.get('project')
    if proj:
        exp = Experiment.query.get(int(proj))
    else:
        exp = None
    return render_template('users.html',proj=exp)

# Show info from user
@dashboardB.route("/info/user")
@dashboardB.route("/info/user/<userid>")
@login_required
def user_info(userid=None):
    if not userid:
        return render_template('error.html',message="Usuario no definido",recent=recent.get())
    user=User.query.filter(User.userid==userid).one()
    if not user:
        return render_template('error.html',message="Usuario existente",recent=recent.get())
    return render_template('user_info.html',user=user,recent=recent.get())


@dashboardB.route("/invite")
@login_required
def experiment_invite():
    return redirect(url_for('dashboard'))

# Media
@dashboardB.route("/media")
@login_required
def media_list():
    return render_template('media.html')


