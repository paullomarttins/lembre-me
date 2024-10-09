from flask import Flask, render_template, url_for, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lembre_me_.sqlite3'
db = SQLAlchemy(app)

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(50), nullable=False)
    observa = db.Column(db.String(200), default=None, nullable=True)
    dt_inicio = db.Column(db.DateTime, default=datetime.now)
    dt_final = db.Column(db.Date, nullable=True)
    dt_priority = db.Column(db.Date, nullable=True)
    priority = db.Column(db.Boolean, default=False)
    progress = db.Column(db.String(20), default="Novo")

    # Função para fins de depuração, retorna o ID
    # def __repr__(self):
    #     return f'<Tarefa: {self.id}>'

    # def __init__(self, content):
    #     self.content = content

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)

    # Pagination retorna apenas 5 registros
    tasks = Tarefa.query.paginate(page=page, per_page=5, error_out=False)
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
            return 'Algo deu errado ao incluir sua tarefa!'
    
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Tarefa.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Algo deu errado ao excluir sua tarefa!'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Tarefa.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        task.progress = request.form['progress']
        task.observa = request.form['observa']

        if not task.content or not task.progress:
            return redirect('/')

        if task.progress == 'Concluído':
            task.dt_final = datetime.now()
        else:
            task.dt_final = None

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Algo deu errado ao atualizar sua tarefa!'
    else:
        return render_template('update.html', task=task)

@app.route('/priority/<int:id>', methods=['GET','POST'])
def priority(id):
    task = Tarefa.query.get_or_404(id)
    
    if not task.dt_final: 
        task.dt_priority = datetime.now()
        task.priority = True
        
    try:
        db.session.commit()
        return redirect('/')
    except:
        return 'Erro ao priorizar Tarefa.'

@app.route('/priority/unpriority/<int:id>', methods=['GET','POST'])
def unpriority(id):
    task = Tarefa.query.get_or_404(id)
    
    if not task.dt_final: 
        task.dt_priority = None
        task.priority = False
        
    try:
        db.session.commit()
        return redirect('/')
    except:
        return 'Erro ao remover prioridade.'

if __name__ == "__main__":
    app.run(debug=True)