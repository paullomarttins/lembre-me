from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc, func
from datetime import datetime
from os import environ
from forms import NewTaskForm, UpdateForm

app = Flask(__name__)
app.secret_key = environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lembre_me.sqlite3'
db = SQLAlchemy(app)

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(50), nullable=False)
    observa = db.Column(db.String(200), default="", nullable=True)
    dt_inicio = db.Column(db.DateTime, default=datetime.now)
    dt_final = db.Column(db.DateTime, nullable=True)
    dt_priority = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, default=0)
    progress = db.Column(db.String(20), default="Novo")
    created_by = db.Column(db.String(20), nullable=False)
    assigned = db.Column(db.String(20), default="", nullable=True)

    # Função para fins de depuração, retorna o ID
    def __repr__(self):
        return f'Tarefa: {self.id}'

    def __init__(self):
        self.content = self.content
        self.created_by = self.created_by

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    my_status = ['Em andamento', 'Pendente', 'Novo']
    form = NewTaskForm()

    # Pagination retorna apenas 5 registros
    tasks = Tarefa.query.order_by(desc(Tarefa.priority)).order_by(asc(Tarefa.dt_priority)).filter(Tarefa.progress.in_(my_status)).paginate(page=page, per_page=5, error_out=False)
    return render_template('index.html', tasks=tasks.items, pagination=tasks, title='Tasks', form=form)

@app.route('/closed')
def closed():
    page = request.args.get('page', 1, type=int)
    my_status = ['Concluído', 'Cancelado']

    tasks = Tarefa.query.filter(Tarefa.progress.in_(my_status)).paginate(page=page, per_page=5, error_out=False)
    return render_template('closed.html', tasks=tasks.items, pagination=tasks, title='Closed')

@app.route('/insert', methods=['POST', 'GET'])
def insert():

    form = NewTaskForm()
    if form.validate_on_submit():
        new_task = Tarefa()
        form.populate_obj(new_task)

        try:
            db.session.add(new_task)
            db.session.commit()
            flash('Tarefa criada com sucesso!')
            return redirect(url_for('index'))
        except:
            flash('Algo deu errado ao incluir sua tarefa!')
            return redirect(url_for('index'))
        else:
            render_template('index.html', form=form)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Tarefa.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        flash(f'{task_to_delete} excluída com sucesso!')
        return redirect(url_for('index'))
    except:
        flash('Algo deu errado ao excluir sua tarefa!')
        return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Tarefa.query.get_or_404(id)
    fl_status = ['Novo', 'Em andamento', 'Pendente', 'Cancelado', 'Concluído']
    form = UpdateForm()
    form.content.data = task.content
    form.created_by.data = task.created_by
    form.assigned.data = task.assigned
    form.observa.data = task.observa

    if request.method == 'POST':
        task.content = request.form['content']
        task.progress = request.form['progress']
        task.assigned = request.form['assigned']
        task.observa = request.form['observa']

        if not task.content or not task.progress:
            return redirect(url_for('index'))

        if task.progress == 'Concluído':
            task.dt_final = datetime.now()
        elif task.progress in fl_status:
            task.progress
        else:
            flash('Erro! Status inserido inválido.')
            return redirect(url_for('index'))

        try:
            db.session.commit()
            flash('Tarefa atualizada com sucesso.')
            return redirect(url_for('index'))
        except:
            flash('Algo deu errado ao atualizar sua tarefa!')
            return redirect(url_for('index'))
    else:
        new_status = [status for status in fl_status if status != task.progress]
        return render_template('update.html', task=task, fl_status=new_status, title='Atualizar', form=form)

@app.route('/priority/<int:id>', methods=['GET','POST'])
def priority(id):
    task = Tarefa.query.get_or_404(id)
    qt_priority = db.session.query(func.sum(Tarefa.priority)).all()
    num_priority = qt_priority[0][0] # Converte a tupla em integer

    # Fixando apenas 3 prioridades
    if num_priority <= 2 and task.progress != 'Pendente' or task.progress != 'Concluído':

        if not task.dt_final:
            task.dt_priority = datetime.now()
            task.priority = 1

        try:
            db.session.commit()
            flash(f'{task} priorizada.')
            return redirect(url_for('index'))
        except:
            flash('Erro ao priorizar Tarefa.')
            return redirect(url_for('index'))
    else:
        flash('Você não pode ter mais de 3 prioridades abertas ou com status "Pendente"')
        return redirect(url_for('index'))

@app.route('/priority/unpriority/<int:id>', methods=['GET','POST'])
def unpriority(id):
    task = Tarefa.query.get_or_404(id)

    if not task.dt_final:
        task.dt_priority = None
        task.priority = 0

    try:
        db.session.commit()
        flash(f'{task} prioridade removida.')
        return redirect(url_for('index'))
    except:
        flash('Erro ao remover prioridade.')
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
