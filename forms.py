from flask_wtf import FlaskForm
from sqlalchemy.sql.compiler import StrSQLCompiler
from wtforms import StringField, SubmitField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired

class NewTaskForm(FlaskForm):
    content = StringField('Título', validators=[DataRequired()])
    created_by = StringField('Criado por', validators=[DataRequired()])
    submit = SubmitField('+')

class UpdateForm(FlaskForm):
    content = StringField('Título da tarefa', validators=[DataRequired()])
    created_by = StringField('Criado Por', validators=[DataRequired()])
    assigned = StringField('Atribuído Para', validators=[DataRequired()])
    observa = TextAreaField('Observação:', validators=[DataRequired()])
    submit = SubmitField('+')
