import os
from flask import Flask, request, url_for, redirect, make_response
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from datetime import datetime
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import bcrypt

cur_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project_database.sqlite3"

db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

class AllUser(db.Model):
    __tablename__ = 'all_user'
    count = db.Column(db.Integer, autoincrement = True, primary_key = True)
    username = db.Column(db.String, nullable = False, unique = True)
    hash = db.Column(db.String, primary_key = True, nullable = False, unique = True)


class CurrentUser(db.Model):
    __tablename__ = 'current_user'
    cur_user_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    user_name = db.Column(db.String, unique = True, nullable = False)

class TodoHeader(db.Model):
    __tablename__ = 'todoHeader'
    todoCount = db.Column(db.Integer, autoincrement = True, primary_key = True)
    todoHeader = db.Column(db.String, nullable = False, unique = True)
    tuserId = db.Column(db.Integer, db.ForeignKey("current_user.cur_user_id"), primary_key = True)
    description = db.Column(db.String, nullable = False)

class List(db.Model):
    __tablename__ = 'list'
    list_index = db.Column(db.Integer, autoincrement = True, primary_key = True)
    list_name = db.Column(db.String, nullable = False, unique = True)
    todo_i = db.Column(db.Integer, db.ForeignKey("todoHeader.todoCount"), primary_key = True)
    todo_u = db.Column(db.Integer, db.ForeignKey("current_user.cur_user_id"), primary_key = True)
    start_time = db.Column(db.Integer, primary_key = True)
    end_time = db.Column(db.Integer, nullable = False)
    completed = db.Column(db.Integer, nullable = False)
    completed_time = db.Column(db.Integer, nullable = False)

@app.route("/", methods = ["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        CurrentUser.query.delete()
        user = db.session.query(AllUser).filter(AllUser.username == username, AllUser.hash == password).first()
        if not user is None:    
            cu = CurrentUser(user_name = username)
            db.session.add(cu)
            db.session.commit()
            return redirect(url_for('Main'))
        else:
            return redirect(url_for('modal2'))
    return render_template("login.html")

@app.route("/login/modal2", methods=["GET","POST"])
def modal2():
    return render_template("modal2.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            user = AllUser(username = username, hash = password)
            db.session.add(user)
        except:
            return redirect(url_for('modal1'))
        else:
            db.session.commit()

        return redirect(url_for('login'))
    return render_template("signup.html")

@app.route("/signup/modal1", methods=["GET","POST"])
def modal1():
    return render_template("modal1.html")


@app.route("/main", methods = ["GET", "POST"])
def Main():
    cu = db.session.query(CurrentUser).first()
    username = cu.user_name
    userid = cu.cur_user_id
    tl = db.session.query(TodoHeader).filter(TodoHeader.tuserId == userid).all()
    task = {}
    for t in tl:
        toc = t.todoCount
        tak = db.session.query(List).filter(List.todo_i == toc).all()
        print(type(tak))
        # print(type(tak[0]))
        list = []
        for l in tak:
            li = []
            if l.completed == 0:
                li.append(l.list_index)
                li.append(l.list_name)
                list.append(li)
        print(list)
        task[toc] = list
        
        

    return render_template("Main.html", username = username, userid = userid, tl = tl, task = task)

@app.route("/addList/<userid>", methods = ["GET", "POST"])
def addList(userid):
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']
        tl = TodoHeader(todoHeader = name, description = desc, tuserId = userid)
        db.session.add(tl)
        db.session.commit()
        return redirect(url_for('Main'))
    return render_template("addList.html", userid = userid)

@app.route("/add_List/<userid>/<todoCount>", methods = ["GET", "POST"])
def add_List(userid,todoCount):
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']
        date = request.form['date']
        element = datetime.strptime(date,'%Y-%m-%d').strftime("%d/%m/%Y")
        element2 = datetime.strptime(element,"%d/%m/%Y")
        timestamp = datetime.timestamp(element2)
        start_time = datetime.now().timestamp()
        task = List(list_name = name, todo_i = todoCount,todo_u = userid, start_time = start_time, end_time = timestamp, completed = 0, completed_time = 0)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('Main'))
    return render_template("add_List.html", todoCount = todoCount, userid = userid)

@app.route("/delete/<userid>/<todoCount>", methods=["GET", "POST"])
def delete(userid,todoCount):
    TodoHeader.query.filter_by(todoCount = todoCount).delete()
    #List.query.filter(todo_i = todoCount, todo_u = userid).delete()
    db.session.query(List).filter(List.todo_i == todoCount, List.todo_u == userid).delete()
    db.session.commit()
    return redirect(url_for('Main'))


@app.route("/delete/<userid>/<todoCount>/<lindex>", methods=["GET", "POST"])
def delete2(userid,todoCount, lindex):
    db.session.query(List).filter(List.list_index == lindex, List.todo_i == todoCount, List.todo_u == userid).delete()
    db.session.commit()
    return redirect(url_for('Main'))

           
@app.route("/update/<userid>/<todoCount>/<lindex>", methods = ["GET", "POST"])
def updateCard(userid, todoCount, lindex):
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']
        date = request.form['date']
        element = datetime.strptime(date,'%Y-%m-%d').strftime("%d/%m/%Y")
        element2 = datetime.strptime(element,"%d/%m/%Y")
        timestamp = datetime.timestamp(element2)
        list = db.session.query(List).filter(List.list_index == lindex).first()
        list.list_name = name
        list.end_time = timestamp
        db.session.add(list)
        db.session.commit()
        return redirect(url_for('Main'))
    return render_template("updateCard.html", userid = userid, todoCount = todoCount, lindex = lindex)

@app.route("/summary/<userid>", methods = ["GET","POST"])
def summary(userid):
    # th = db.session.query(TodoHeader).filter(TodoHeader.tuserId == userid).all()
    list = db.session.query(List).filter(List.todo_u == userid).all()
    total_task = 0
    completed = 0
    default = 0
    pending = 0
    x = []
    y = []
    z = []
    w = []
    i = 1
    cur_time = datetime.now().timestamp()
    graph = './static/plot.png'
    graph1 = './static/plot2.png'
    for l in list:
        w.append(i)
        i += 1
        dt1 = datetime.fromtimestamp(l.start_time)
        dt2 = datetime.fromtimestamp(l.end_time)
        dt6 = datetime.fromtimestamp(cur_time)
        dt4 = dt2 - dt1
        dt7 = dt6 - dt1
        if dt4.days >= 0:
            z.append(dt4.days)
            y.append(0)
        else:
            z.append(0)
            y.append(dt7.days)
        
        total_task += 1
        if l.completed == 1:
            completed += 1
            dt3 = datetime.fromtimestamp(l.completed_time)
            dt5 = dt3 - dt1
            x.append(dt5.days)
        else:
            x.append(0)
            if l.end_time <= cur_time:
                default += 1
            else:
                pending += 1
    # a = np.array([completed, default, pending])
    # b = ["completed", "default", "pending"]
    # plt.pie(a,labels=b)
    # plt.savefig(graph)
    fig,ax = plt.subplots(figsize=(10,7))
    ax.bar(w,x,color='green',width=0.2, label='completed')
    ax.bar(w,z,color='red',width=0.2, label='deadline')
    ax.bar(w,y,color='y', width=0.2, label='default')
    plt.xlabel("tasks", fontweight='bold', fontsize=25)
    plt.ylabel("difference", fontweight='bold', fontsize = 25)
    plt.legend(loc='best')
    plt.savefig(graph1)
    return render_template("summary.html", total_task = total_task, completed = completed, default = default, pending = pending, graph = graph)

@app.route("/completed/<userid>/<todoCount>/<lindex>")
def completed(userid, todoCount, lindex):
    list = db.session.query(List).filter(List.list_index == lindex, List.todo_i == todoCount, List.todo_u == userid).first()
    list.completed = 1
    list.completed_time = datetime.now().timestamp()
    db.session.add(list)
    db.session.commit()
    return redirect(url_for('Main'))


if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        debug = True,
        port = 8080
    )