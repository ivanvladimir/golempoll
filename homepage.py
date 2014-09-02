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
    Flask,
    redirect,
    jsonify,
    url_for,
    render_template,
    request
    )
from flask.ext.login import (
    LoginManager,
    login_user,
    logout_user,
    login_required)
from flask.ext.triangle import Triangle
from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, validators, SelectField, IntegerField

# Extra libraries
from yaml import load, dump
import time
import uuid

# App imports
from User import User

app = Flask('homepage')
Triangle(app)
app.config.from_pyfile('homepage.cfg')

login_manager = LoginManager()
login_manager.init_app(app)


# Formas
class ExperimentF(Form):
    name         = StringField('Nombre', [validators.Length(min=4, max=255),validators.DataRequired()])
    description  = StringField(u'Descripción', [validators.Length(min=4,max=255),validators.DataRequired()])
    content      = TextAreaField(u'Definición del experimento')
    invitation   = TextAreaField(u'Texto para invitación')
    instructions = TextAreaField(u'Instrucciones experimento')
    save         = SubmitField("Guardar")
    cancel       = SubmitField("Cancelar")

class UserF(Form):
    birthday     = IntegerField(u'Año de nacimiento', [validators.DataRequired()])
    level        = SelectField(u'Escolaridad', 
                            [validators.DataRequired()],
                        choices=[('prim',u'Primaria'),('sec',u'Secunadaria'),('prep',u'Prepa'),('uni',u'Universidad'),('pos',u'Posgrado')])
    previous_ex  = SelectField(u'Experiencia previa con robots',
                            [validators.DataRequired()],
                        choices=[('no',u'No'),('yes',u'Sí')])
    save         = SubmitField("Guardar")
    cancel       = SubmitField("Cancelar")

class UserInviteF(Form):
    correo       = StringField(u'Dirección electrónica', [validators.DataRequired(),validators.Email()])
    save         = SubmitField("Enviar")
    cancel       = SubmitField("Cancelar")


def save_users(USERS):
    with open(app.config['USERS_FILE'],"w") as usersf:
        dump(dict([ (k,v) for k, v in USERS.iteritems()]),usersf)

def save_exps(EXPS):
    with open(app.config['EXPERIMENTS_FILE'],"w") as expssf:
        dump(dict([ (k,v) for k, v in EXPS.iteritems()]),expssf)


# Loading users
with open(app.config['USERS_FILE']) as usersf:
    USERS = dict([ (k,User(k,v)) for k, v in load(usersf).iteritems()])

# Loading experiments
with open(app.config['EXPERIMENTS_FILE']) as expsf:
    EXPS = dict([ (k,v) for k, v in load(expsf).iteritems()])

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
    return render_template('adminindex.html')

# Managing users
@app.route("/dashboard/create/user")
def user_new():
    u=uuid.uuid4()
    userid=str(u)
    USERS[userid]={}
    USERS[userid]['user']=User(userid,[])
    USERS[userid]['confirmed']=False
    save_users(USERS)
    return render_template('user_created.html',userid=userid)

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
        EXPS[expid]['content']=load(form.content.data)
        EXPS[expid]['name']=form.name.data
        EXPS[expid]['description']=form.description.data
        EXPS[expid]['date_creation']=time.time()
        EXPS[expid]['date_modification']=time.time()
        EXPS[expid]['status']=False

        save_exps(EXPS)

        return redirect('/dashboard/info/experiment/'+expid)
    else:
        return render_template('experiment_edit.html',form=form)

@app.route("/dashboard/invite/user/<userid>", methods=['GET','POST'])
def user_invite_userid(userid):
    try:
        if USERS[userid]['confirmed']:
            return render_template('error.html',message="Usuario existente")
    except KeyError:
            return render_template('error.html',message="Usuario inexperado")
    form=UserInviteF(request.form)
    if form.cancel.data:
        return redirect(url_for(dashboard))
    if form.validate_on_submit():
        return redirect('/dashboard/info/user/'+userid)
    else:
        return render_template('email_edit.html',form=form)


@app.route("/dashboard/invite/user", methods=['GET','POST'])
def user_invite():
    form=UserInviteF(request.form)
    if form.cancel.data:
        return redirect(url_for(dashboard))
    if form.validate_on_submit():
        u=uuid.uuid4()
        userid=str(u)
        USERS[userid]={}
        USERS[userid]['confirmed']=False
        USERS[userid]['user']=User(userid,[])

        return redirect('/dashboard/info/user/'+userid)
    else:
        return render_template('email_edit.html',form=form)

@app.route("/confirm/<userid>", methods=['GET','POST'])
def user_cofirmation(userid):
    try:
        if USERS[userid]['confirmed']:
            return render_template('error.html',message="Usuario existente")
    except KeyError:
            return render_template('error.html',message="Usuario inexperado")

    form=UserF(request.form)
    if form.cancel.data:
        return redirect(url_for(dashboard))
    if form.validate_on_submit():
        USERS[userid]['confirmed']=True
        USERS[userid]['birthday']=form.birthday.data
        USERS[userid]['level']=form.level.data
        USERS[userid]['prev']=form.previous_ex.data

        save_users(USERS)

        return redirect('/dashboard/info/user/'+userid)
    else:
        return render_template('user_info_edit.html',form=form,userid=userid)





@app.route("/dashboard/info/experiment/<expid>")
def experiment_info(expid):
    if not EXPS.has_key(expid):
        return render_template('error.html',message="Experimento no definido")
    return render_template('experiment_info.html',exp=EXPS[expid])

@app.route("/dashboard/info/user/<expid>")
def user_info(expid):
    if not USERS.has_key(expid):
        return render_template('error.html',message="Experimento no definido")
    return render_template('user_info.html',user=USERS[expid])


@app.route("/dashboard/delete/experiment/<expid>")
def experiment_delete(expid):
    if not EXPS.has_key(expid):
        return render_template('error.html',message="Experimento no definido")
    del EXPS[expid]
    return render_template('/dashboard')



@app.route("/dashboard/list/experiment")
def experiment_list():
    return render_template('experiments.html',exps=EXPS,strftime=time.strftime)

@app.route("/dashboard/experiments.json")
def experiment_json():
    return jsonify(EXPS)

@app.route("/dashboard/list/user")
def user_list():
    return render_template('users.html',users=USERS,strftime=time.strftime)




@app.route("/dashboard/clone/experiment/<expid>")
def experiment_clone2(expid):
    u=uuid.uuid4()
    expid_=str(u)
    EXPS[expid_]={}
    EXPS[expid_]['content']= EXPS[expid]['content']
    EXPS[expid_]['name']=EXPS[expid]['name']
    EXPS[expid_]['description']= EXPS[expid]['description']
    EXPS[expid_]['date_creation']=time.time()
    EXPS[expid_]['date_modification']=time.time()
    EXPS[expid]['status']=False

    save_exps(EXPS)

    return redirect('/dashboard/info/experiment/'+expid)

@app.route("/dashboard/on/experiment/<expid>")
def experiment_on(expid):
    EXPS[expid]['status']=True
    with open(app.config['EXPERIMENTS_FILE'],"w") as expsf:
        dump(dict([ (k,v) for k, v in EXPS.iteritems()]),expsf)

    return redirect('/dashboard/info/experiment/'+expid)

@app.route("/dashboard/off/experiment/<expid>")
def experiment_offf(expid):
    EXPS[expid]['status']=False
    save_exps(EXPS)

    return redirect('/dashboard/info/experiment/'+expid)


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

