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
    request,
    make_response,
    flash
    )
from flask.ext.login import (
    LoginManager,
    login_user,
    current_user,
    logout_user,
    login_required)
from flask.ext.triangle import Triangle
from flask_wtf import Form
from wtforms import (
    StringField, 
    TextAreaField, 
    SubmitField, 
    validators, 
    SelectField,
    PasswordField, 
    IntegerField)

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

class LoginF(Form):
    admin    = StringField('Administrador', [validators.Required()])
    password = PasswordField('Password', [])
    save     = SubmitField("Entrar")

class UserF(Form):
    birthday     = IntegerField(u'Año de nacimiento', [validators.DataRequired()])
    level        = SelectField(u'Escolaridad', 
                            [validators.DataRequired()],
                        choices=[('prim',u'Primaria'),('sec',u'Secunadaria'),('prep',u'Prepa'),('uni',u'Universidad'),('pos',u'Posgrado')])
    genero       = SelectField(u'Género',
                            [validators.DataRequired()],
                        choices=[('M',u'Masculino'),('F',u'Fememino')])
    previous_ex  = SelectField(u'Experiencia previa con robots',
                            [validators.DataRequired()],
                        choices=[('no',u'No'),('yes',u'Sí')])
    save         = SubmitField("Guardar")
    cancel       = SubmitField("Cancelar")

class UserInviteF(Form):
    email       = StringField(u'Dirección electrónica', [validators.DataRequired(),validators.Email()])
    save         = SubmitField("Enviar")
    cancel       = SubmitField("Cancelar")


def save_users(USERS):
    with open(app.config['USERS_FILE'],"w") as usersf:
        dump(dict([ (k,v) for k, v in USERS.iteritems()]),usersf)

def save_exps(EXPS):
    with open(app.config['EXPERIMENTS_FILE'],"w") as expssf:
        dump(dict([ (k,v) for k, v in EXPS.iteritems()]),expssf)

def save_answers(ANS):
    with open(app.config['ANSWERS_FILE'],"w") as ansf:
        dump(ANS,ansf)

def save_candidates(CNDS):
    with open(app.config['CANDIDATES_FILE'],"w") as canf:
        dump(CNDS,canf)


# Loading users
with open(app.config['USERS_FILE']) as usersf:
    USERS = dict([(k,v) for k, v in load(usersf).iteritems()])

# Loading experiments
with open(app.config['EXPERIMENTS_FILE']) as expsf:
    EXPS = dict([ (k,v) for k, v in load(expsf).iteritems()])

# Loading answers
with open(app.config['ANSWERS_FILE']) as ansf:
    ANS = load(ansf)

# Loading candidates
with open(app.config['CANDIDATES_FILE']) as canf:
    CNDS = load(canf)

# Loading admins
with open(app.config['ADMINS_FILE']) as admf:
    ADMS = load(admf)
    ADMS_ = dict([ (id,User(id)) for id,pw in ADMS])

# Managin login
@login_manager.user_loader
def load_user(userid):
    try:
        return USERS[userid]['user']
    except KeyError:
      return ADMS_[id]
    except KeyError:
        return None

       

# Managing Administradores
@app.route("/login", methods=["GET", "POST"])
def login_admin():
    form = LoginF()
    if form.validate_on_submit():
        user=[ i for i,(x,y) in enumerate(ADMS) if x==form.admin.data 
                                               and y==form.password.data]
        if len(user)==1:
            login_user(load_user(form.admin.data))
            return redirect("/dashboard")
        else:
            flash('Problema con entrada')
            return redirect("/")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

# Managing dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('adminindex.html')

# Managing users
@app.route("/dashboard/create/user")
@login_required
def user_new():
    u=uuid.uuid4()
    userid=str(u)
    USERS[userid]={}
    USERS[userid]['user']=User(userid,[])
    USERS[userid]['info']={}
    USERS[userid]['info']['confirmed']=False
    USERS[userid]['info']['exps']=[]
    save_users(USERS)
    return render_template('user_created.html',userid=userid)

# Managing experiments
@app.route("/dashboard/create/experiment", methods=['GET','POST'])
@login_required
def experiment_new():
    form=ExperimentF(request.form)
    if form.cancel.data:
        return redirect(url_for(dashboard))
    if form.validate_on_submit():
        u=uuid.uuid4()
        expid=str(u)
        EXPS[expid]={}
        EXPS[expid]['content']=load(form.content.data)
        EXPS[expid]['instructions']=load(form.instructions.data)
        EXPS[expid]['invitation']=load(form.invitation.data)
        EXPS[expid]['name']=form.name.data
        EXPS[expid]['description']=form.description.data
        EXPS[expid]['date_creation']=time.time()
        EXPS[expid]['date_modification']=time.time()
        EXPS[expid]['status']=False

        save_exps(EXPS)

        return redirect('/dashboard/info/experiment/'+expid)
    else:
        return render_template('experiment_edit.html',form=form,type='create')



@app.route("/dashboard/edit/experiment/<expid>", methods=['GET','POST'])
@login_required
def experiment_edit(expid):
    if not EXPS.has_key(expid):
        return render_template('error.html',message="Experimento no definido")
    form=ExperimentF(request.form)
    if form.cancel.data:
        return redirect(url_for(dashboard))
    if form.validate_on_submit():
        EXPS[expid]['content']=load(form.content.data)
        EXPS[expid]['name']=form.name.data
        EXPS[expid]['instructions']=load(form.instructions.data)
        EXPS[expid]['invitation']=load(form.invitation.data)
        EXPS[expid]['description']=form.description.data
        EXPS[expid]['date_modification']=time.time()
        EXPS[expid]['status']=False
        save_exps(EXPS)
        return redirect('/dashboard/info/experiment/'+expid)
    else:
        form.content.data=dump(EXPS[expid]['content'])
        form.name.data=EXPS[expid]['name']
        form.description.data=EXPS[expid]['description']
        return render_template('experiment_edit.html',
                form=form,type='edit',expid=expid)



@app.route("/dashboard/invite/user/<userid>")
@login_required
def user_invite_userid(userid):
    project = request.cookies.get('project')
    if not project:
        return render_template('error.html',message="Projecto no seleccionado")
    try:
        USERS[userid]['info']['confirmed']
    except KeyError:
            return render_template('error.html',message="Usuario inexperado")
    try:
        USERS[userid]['info']['experiments'].append(project)
    except KeyError:
        USERS[userid]['info']['experiments']=[project]
        save_users(USERS)
    USERS[userid]['info']['experiments']=[project]
    return redirect('/dashboard/info/user/'+userid)


@app.route("/dashboard/invite/user", methods=['GET','POST'])
@login_required
def user_invite():
    project = request.cookies.get('project')
    if not project:
        return render_template('error.html',message="Projecto no seleccionado")
    form=UserInviteF(request.form)
    if form.cancel.data:
        return redirect(url_for(dashboard))
    if form.validate_on_submit():
        u=uuid.uuid4()
        userid=str(u)
        USERS[userid]={}
        USERS[userid]['info']={}
        USERS[userid]['info']['confirmed']=False
        USERS[userid]['info']['experiments']=[project]
        USERS[userid]['info']['email']=form.email.data
        USERS[userid]['user']=User(userid,[])
        save_users(USERS)
        return redirect('/dashboard/info/user/'+userid)
    else:
        return render_template('email_edit.html',form=form)

@app.route("/confirm/<userid>", methods=['GET','POST'])
@login_required
def user_cofirmation(userid):
    try:
        if USERS[userid]['info']['confirmed']:
            return render_template('error.html',message="Usuario existente")
    except KeyError:
            return render_template('error.html',message="Usuario inexperado")

    form=UserF(request.form)
    if form.cancel.data:
        return redirect(url_for(dashboard))
    if form.validate_on_submit():
        USERS[userid]['info']['confirmed']=True
        USERS[userid]['info']['birthday']=form.birthday.data
        USERS[userid]['info']['level']=form.level.data
        USERS[userid]['info']['prev']=form.previous_ex.data
        USERS[userid]['info']['gender']=form.genero.data
        save_users(USERS)

        return redirect('/'+userid)
    else:
        return render_template('user_info_edit.html',form=form,userid=userid)

@app.route("/dashboard/info/experiment/<expid>")
@login_required
def experiment_info(expid):
    if not EXPS.has_key(expid):
        return render_template('error.html',message="Experimento no definido")
    return render_template('experiment_info.html',exp=EXPS[expid])

@app.route("/dashboard/info/user/<expid>")
@login_required
def user_info(expid):
    if not USERS.has_key(expid):
        return render_template('error.html',message="Experimento no definido")
    return render_template('user_info.html',user=USERS[expid])


@app.route("/dashboard/delete/experiment/<expid>")
@login_required
def experiment_delete(expid):
    if not EXPS.has_key(expid):
        return render_template('error.html',message="Experimento no definido")
    del EXPS[expid]
    return redirect('/dashboard')


@app.route("/dashboard/select/experiment/<expid>")
@login_required
def experiment_select(expid):
    if not EXPS.has_key(expid):
        return render_template('error.html',message="Experimento no definido")
    resp = make_response(render_template('adminindex.html'))
    resp.set_cookie('project', expid)
    resp.set_cookie('project_name', EXPS[expid]['name'])
    return resp

@app.route("/dashboard/cerrar/experiment")
@login_required
def experiment_close():
    resp = make_response(render_template('adminindex.html'))
    resp.set_cookie('project', "",expires=0)
    resp.set_cookie('project_name', "",expires=0)
    return resp



@app.route("/dashboard/list/experiment")
@login_required
def experiment_list():
    return render_template('experiments.html',exps=EXPS)

@app.route("/dashboard/experiments.json")
@login_required
def experiment_json():
    return jsonify(EXPS)

@app.route("/dashboard/users.json")
def user_json():
    return jsonify(dict([(k,v['info']) for k,v in USERS.iteritems()]))


@app.route("/dashboard/list/user")
def user_list():
    return render_template('users.html',users=USERS)




@app.route("/dashboard/clone/experiment/<expid>")
@login_required
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
@login_required
def experiment_on(expid):
    EXPS[expid]['status']=True
    with open(app.config['EXPERIMENTS_FILE'],"w") as expsf:
        dump(dict([ (k,v) for k, v in EXPS.iteritems()]),expsf)

    return redirect('/dashboard/info/experiment/'+expid)

@app.route("/dashboard/off/experiment/<expid>")
@login_required
def experiment_offf(expid):
    EXPS[expid]['status']=False
    save_exps(EXPS)

    return redirect('/dashboard/info/experiment/'+expid)


@app.route("/dashboard/invite")
@login_required
def experiment_invite():
    return redirect(dashboard)

@app.route("/dashboard/live/<expid>")
@login_required
def experiment_live():
    return redirect(dashboard)


@app.route("/poll")
@login_required
def poll():
    return render_template('poll.html'),


@app.route("/",methods=['GET','POST'])
def main():
    form=UserInviteF(request.form)
    if form.validate_on_submit():
        u=uuid.uuid4()
        userid=str(u)
        CNDS[userid]={}
        CNDS[userid]['email']=form.email.data
        CNDS[userid]['confirmed']=False
        save_candidates(CNDS)
        return redirect('/')
    else:
        return render_template('index.html',form=form, active=True)

@app.route("/api/poll/<expid>")
def poll_json(expid):
    return jsonify(EXPS[expid]['content'])

@app.route("/api/poll/<expid>/option",methods=['POST'])
def push_json(expid):
    option = request.args.get('emotion', '')
    answer = request.args.get('answer', '')
    try:
        ANS[expid].append((option,answer))
    except KeyError:
        ANS[expid]=[(option,answer)]

@app.route("/finish")
@login_required
def finish_poll():
    save_answers(ANS)
    USERS[current_user.get_id()]['info']['experiments'].pop(0)
    return redirect('/')

# Managing experiments
@app.route("/<iduser>")
def login(iduser):
    if  not len(USERS[iduser]['info']['experiments'])>0:
        return render_template('error.html',message="Lo sentimos no hay ningun experimento asignado")
    user=load_user(iduser)
    if user:
        login_user(user)
        resp = make_response(render_template('poll_prev.html',
                        instructions=EXPS[USERS[user.get_id()]['info']['experiments'][0]]['instructions']) )
        resp.set_cookie('running_exp', USERS[user.get_id()]['info']['experiments'][0])
        return resp
    else:
        return redirect('/')



# Managing experiments
if __name__ == '__main__':
    app.debug = True;
    app.run()

