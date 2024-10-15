from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc, func
from datetime import datetime
from os import environ

app = Flask(__name__)
app.secret_key = environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lembre_me.sqlite3'
db = SQLAlchemy(app)

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(50), nullable=False)
    observa = db.Column(db.String(200), default=None, nullable=True)
    dt_inicio = db.Column(db.DateTime, default=datetime.now)
    dt_final = db.Column(db.DateTime, nullable=True)
    dt_priority = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, default=0)
    progress = db.Column(db.String(20), default="Novo")

    # Função para fins de depuração, retorna o ID
    def __repr__(self):
        return f'<Tarefa: {self.id}>'

    # def __init__(self, content):
    #     self.content = content

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)

    # Pagination retorna apenas 5 registros
    tasks = Tarefa.query.order_by(desc(Tarefa.priority)).order_by(asc(Tarefa.dt_priority)).paginate(page=page, per_page=5, error_out=False)
    return render_template('index.html', tasks=tasks.items, pagination=tasks)

@app.route('/insert', methods=['POST', 'GET'])
def insert():
    if request.method == 'POST':
        
        task_content = request.form['content']
        new_task = Tarefa(content=task_content)    

        if not task_content:
            return redirect('/')

        try:       
            db.session.add(new_task)
            db.session.commit()            
            return redirect(url_for('index'))
        except:
            flash('Algo deu errado ao incluir sua tarefa!')
            return redirect(url_for('index'))
    
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Tarefa.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        flash('Algo deu errado ao excluir sua tarefa!')
        return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Tarefa.query.get_or_404(id)
    fl_status = ['Em andamento', 'Pendente', 'Cancelado', 'Concluído']

    if request.method == 'POST':
        task.content = request.form['content']
        task.progress = request.form['progress']
        task.observa = request.form['observa']

        if not task.content or not task.progress:
            return redirect('/')

        if task.progress == 'Concluído':
            task.dt_final = datetime.now()
        elif task.progress == 'Cancelado':
            task.progress = 'Cancelado'
        elif task.progress == 'Pendente':
            task.progress = 'Pendente'
        elif task.progress == 'Em andamento':
            task.progress = 'Em andamento'
        else:
            #task.dt_final = None
            flash('Erro! Status inserido inválido.')
            return redirect('/')

        try:
            db.session.commit()
            return redirect('/')
        except:
            flash('Algo deu errado ao atualizar sua tarefa!')
            return redirect(url_for('index'))
    else:
        return render_template('update.html', task=task, fl_status=fl_status)

@app.route('/priority/<int:id>', methods=['GET','POST'])
def priority(id):
    task = Tarefa.query.get_or_404(id)
    qt_priority = db.session.query(func.sum(Tarefa.priority)).all()
    num_priority = qt_priority[0][0] # Converte a tupla em integer

    # Fixando apenas 3 prioridades
    if num_priority <= 2 and task.progress != 'Pendente': 

        if not task.dt_final: 
            task.dt_priority = datetime.now()
            task.priority = 1
            
        try:
            db.session.commit()
            return redirect('/')
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
        return redirect('/')
    except:
        flash('Erro ao remover prioridade.')
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)