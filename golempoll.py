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
from flask import Flask, url_for, redirect, render_template
from flask.ext.login import LoginManager
from flask.ext.triangle import Triangle
from flask.ext.mail import Mail
from  flask.ext.restless import APIManager
from flask.ext.login import (
    login_user,
    logout_user,
    login_required)

# Local import
from dashboard import dashboardB
from poll import pollB
from api import apiB

# Load database
from database import db_session
from models import Admin, User, Experiment, ExperimentUser
from forms import LoginF

# Setting the WebAPP

app = Flask('homepage')
app.register_blueprint(dashboardB,url_prefix='/dashboard')
app.register_blueprint(pollB)
app.register_blueprint(apiB,url_prefix='/api')

# Adding RESTful-Restless api
manager = APIManager(app, session=db_session)
api_experiment=manager.create_api_blueprint(
    Experiment,methods=['GET'],
    collection_name='experiment',
    include_columns=['status','id','name','description','date_creation','date_modification','users','definition']
)
app.register_blueprint(api_experiment,url_prefix='/api')
api_user=manager.create_api_blueprint(
    User,methods=['GET'],
    collection_name='user',
    include_columns=['accepted','confirmed','id','userid','email','gender','year_birthday','experiments']
)
app.register_blueprint(api_user,url_prefix='/api')
Triangle(app)

app.config.from_pyfile('golempoll.cfg')
mail=Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)




# Setting the database
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Managin login
@login_manager.user_loader
def load_user(userid):
    try:
        user=User.query.get(userid)
    except :
        try:
            user=Admin.query.filter(Admin.id==userid).one()
        except:
            return None
    return user

@login_manager.request_loader
def load_user_from_request(request):

    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None

# Entrada a administradores
@app.route("/login", methods=["GET", "POST"])
def login_admin():
    form = LoginF()
    if form.cancel.data:
        return redirect(url_for('index'))
    elif form.validate_on_submit():
        admin = Admin.query.filter(Admin.name==form.admin.data).one()
        if admin.check_passwd(form.password.data):
            admin.authenticated = True
            db_session.add(admin)
            db_session.commit()
            login_user(admin, remember=True)
            return redirect(url_for('dashboard.dashboard'))
        else:
            return render_template("error.html", message="Nombre o password incorrecto")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('poll.index'))

# Managing experiments
if __name__ == '__main__':
    app.debug = True;
    app.run()

