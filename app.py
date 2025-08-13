from flask import Flask, render_template, request,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import pytz

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.template_filter('to_ist')
def to_ist(utc_dt):

    if utc_dt is None:
        return "No Date"
    ist_timezone = pytz.timezone('Asia/Kolkata')
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    return utc_dt.astimezone(ist_timezone)


class Todo(db.Model):
     sno = db.Column(db.Integer, primary_key= True)
     title = db.Column(db.String(200), nullable= False)
     desc = db.Column(db.String(200), )
     date = db.Column(db.DateTime(timezone=True), server_default=func.now())
     status = db.Column(db.String(20), nullable=False, default='Incomplete')

     def __repr__(self):
         return f"{self.sno} - {self.title}"

@app.route("/", methods = ['GET', 'POST'])
def home():
    if request.method=='POST':
        todo = Todo(title = request.form['title'], desc = request.form['desc'])
        db.session.add(todo)
        db.session.commit()
    allTodo = Todo.query.all()
    incomplete_todos = Todo.query.filter_by(status='Incomplete').all()
    completed_todos = Todo.query.filter_by(status='Done').all()

    return render_template('index.html',allTodo = allTodo,
                           incomplete_todos=incomplete_todos, 
                           completed_todos=completed_todos)

def show():
    allTodo = Todo.query.all()
    print(allTodo)
    return render_template("index.html")

@app.route("/update/<int:sno>", methods = ['GET', 'POST'])
def update(sno):
    if request.method=='POST':
        todo = Todo.query.filter_by(sno = sno).first()
        title = request.form['title']
        desc = request.form['desc']
        todo.title= title
        todo.desc= desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/")

    todo = Todo.query.filter_by(sno = sno).first()
    return render_template("update.html",todo = todo)

@app.route("/delete/<int:sno>")
def delete(sno):
    todo = Todo.query.filter_by(sno = sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")

@app.route("/done/<int:sno>")
def mark_as_done(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if todo:
        todo.status = 'Done'
        db.session.add(todo)
        db.session.commit()
    return redirect("/")

if __name__ == ("__main__"):
    with app.app_context():
        db.create_all() 
    app.run(debug=True)