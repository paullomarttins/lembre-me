from flask import Flask, render_template, url_for, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lembre_me.sqlite3'
db = SQLAlchemy(app)

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    observa = db.Column(db.String(1000), nullable=True)
    dt_inicio = db.Column(db.DateTime, default=datetime.now)
    dt_final = db.Column(db.Date, default=None)
    dt_priority = db.Column(db.Date, default=None)
    priority = db.Column(db.Boolean, default=False)
    progress = db.Column(db.String(100), default="Novo")
    
    # def __repr__(self):
    #     return 'Tarefa %r' % self.id

with app.app_context():
    db.create_all()

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        
        task_content = request.form['content']
        new_task = Tarefa(content=task_content)
        
        if not task_content:
            return redirect('/')
        
        try:       
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'Algo deu errado ao incluir sua tarefa!'
    else:
        tasks = Tarefa.query.order_by(Tarefa.dt_inicio).all()
        return render_template('index.html', tasks=tasks) 

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

        if task.progress == 'Concluído' or task.progress == 'Pendente':
            task.dt_final = datetime.now()
            task.dt_priority = datetime.now()
        else:
            task.dt_final = None

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Algo deu errado ao atualizar sua tarefa!'

    else:
        return render_template('update.html', task=task)

if __name__ == "__main__":
    app.run(debug=True)