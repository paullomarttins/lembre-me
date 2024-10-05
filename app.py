from flask import Flask, render_template, url_for, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lembre_me.sqlite3'
db = SQLAlchemy(app)

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    observa = db.Column(db.String(1000), nullable=False)
    dt_inicio = db.Column(db.DateTime, default=datetime.now)
    dt_final = db.Column(db.Date, nullable=False)
    dt_priority = db.Column(db.Date, nullable=False)
    priority = db.Column(db.Boolean, default=False)
    progress = db.Column(db.String(100), default="Novo")

    # Função para fins de depuração, retorna o ID
    # def __repr__(self):
    #     return f'<Tarefa: {self.id}>'

with app.app_context():
    db.create_all()

@app.route('/', methods=['POST', 'GET'])
def index():
    page = request.args.get('page', 1, type=int)
    
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
        # Pagination traz apenas 5 registros
        tasks = Tarefa.query.paginate(page=page, per_page=5, error_out=False)
        #tasks = pagination.items
        return render_template('index.html', tasks=tasks.items, pagination=tasks)

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

if __name__ == "__main__":
    app.run(debug=True)