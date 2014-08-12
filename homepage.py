#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# polling system for golem
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


# Flask imports
from flask import (
    Flask,
    redirect, 
    url_for,
    render_template,
    request
    )
from flask.ext.login import (
    LoginManager,
    login_user,
    logout_user,
    login_required)
from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length, DataRequired

# Extra libraries
from yaml import load, dump
import uuid

# App imports
from User import User

app = Flask('homepage')
app.config.from_pyfile('homepage.cfg')

login_manager = LoginManager()
login_manager.init_app(app)


# Formas
class ExperimentF(Form):
    name    = StringField('Nombre', [Length(min=4, max=255),DataRequired()])
    content = TextAreaField(u'Definición del experimento')
    save=SubmitField("Guardar")
    cancel=SubmitField("Cancelar")

# Loading users
with open(app.config['USERS_FILE']) as usersf:
    USERS = dict([ (k,User(k,v)) for k, v in load(usersf).iteritems()])

# Loading experiments
with open(app.config['EXPERIMENTS_FILE']) as usersf:
    EXPS = dict([ (k,User(k,v)) for k, v in load(usersf).iteritems()])

# Managin login
@login_manager.user_loader
def load_user(userid):
    try:
        return USERS[userid]
    except KeyError:
        return None
        

# Managing dashboard
@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

# Managing users
@app.route("/dashboard/create/user")
def user_new():
    u=uuid.uuid4()
    userid=str(u)
    USERS[userid]=User(userid,[])
    with open(app.config['USERS_FILE'],"w") as usersf:
        dump(dict([ (k,v.data) for k, v in USERS.iteritems()]),usersf)
    return u"new user"

# Managing experiments
@app.route("/dashboard/create/experiment", methods=['GET','POST'])
def experiment_new():
    form=ExperimentF(request.form)
    if form.cancel.data:
        return redirect(url_for(dashboard))
    if form.validate_on_submit():
        u=uuid.uuid4()
        expid=str(u)
        EXPS[expid]={}
        EXPS[expid]['content']=form.content.data
        EXPS[expid]['content']=form.name.data
        with open(app.config['EXPERIMENTS_FILE'],"w") as expsf:
            dump(dict([ (k,v.data) for k, v in USERS.iteritems()]),expsf)

        return redirect('/dashboard/info/experiment/'+expid)
    else:
        return render_template('experiment_edit.html',form=form)


    return u"new experiments"



@app.route("/dashboard/info/experiment/<expid>")
def experiment_info(expid):
     return str(EXPS[expid])



@app.route("/list/experiments")
def experiment_list():
    return render_template('experiments.html',EXPS)




@app.route("/dashboard/invite")
def experiment_invite():
    return redirect(dashboard)

@app.route("/dashboard/live/<expid>")
def experiment_live():
    return redirect(dashboard)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("user"))
 

@app.route("/user")
@login_required
def user():
    return "You are in"
 
# Managing users
@app.route("/<iduser>")
def login(iduser):
    user=load_user(iduser)
    if user:
        login_user(user)
        return redirect(url_for("user"))
    else:
        return "No usuario" 
 

# Managing experiments
if __name__ == '__main__':
    app.debug = True;
    app.run()

