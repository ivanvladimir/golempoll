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
from flask_wtf import Form
from wtforms import (
    StringField, 
    SubmitField, 
    IntegerField,
    SelectField,
    TextAreaField,
    validators, 
    PasswordField)


# Formas
class LoginF(Form):
    admin    = StringField('Administrador', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])
    save     = SubmitField("Entrar")
    cancel   = SubmitField("Cancelar")

class UserF(Form):
    year_birthday   = IntegerField(u'Año de nacimiento', [validators.DataRequired()])
    level      = SelectField(u'Escolaridad', 
                        [validators.DataRequired()],
                        choices=[('prim',u'Primaria'),('sec',u'Secunadaria'),('prep',u'Prepa'),('uni',u'Universidad'),('pos',u'Posgrado')])
    gender     = SelectField(u'Género',
                        [validators.DataRequired()],
                        choices=[('M',u'Masculino'),('F',u'Fememino')])
    previous   = SelectField(u'Experiencia previa con robots',
                        [validators.DataRequired()],
                        choices=[('no',u'No'),('yes',u'Sí')])
    save       = SubmitField("Guardar")
    cancel     = SubmitField("Cancelar")

class UserInviteF(Form):
    email  = StringField(u'Dirección electrónica', [validators.DataRequired(),validators.Email()])
    save   = SubmitField("Enviar")
    cancel = SubmitField("Cancelar")

# Formas
class ExperimentF(Form):
    name         = StringField('Nombre', [validators.Length(min=4, max=255),validators.DataRequired()])
    description  = StringField(u'Descripción', [validators.Length(min=4,max=255),validators.DataRequired()])
    definition   = TextAreaField(u'Definición del experimento')
    invitation   = TextAreaField(u'Texto para invitación')
    instructions = TextAreaField(u'Instrucciones experimento')
    save         = SubmitField("Guardar")
    cancel       = SubmitField("Cancelar")
