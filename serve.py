from flask import Flask, render_template, session, redirect, request, url_for
from flask_session import Session
from tempfile import gettempdir
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
import hashlib
from sqlalchemy.orm import sessionmaker

from functools import wraps
from flask import request, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["user_id"] is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
server.ehlo()
server.login("dembanakh01@gmail.com", "torres2001portu")

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


app = Flask(__name__)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#Session(app)

Base = declarative_base()

class Gamers(Base):
    __tablename__ = "gamers"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), nullable=False)
    hash = Column(String(80), nullable=False)
    mail = Column(String(80), nullable=False)
    ttt = Column(Integer, default=0)
    snake = Column(Integer, default=0)
    
engine = create_engine('sqlite:///gamers.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
sess = DBSession()

ttt_best = 0
snake_best = 0
ttt_bests_prev = []
snake_bests_prev = []
ttt_bests = []
snake_bests = []

for i in range(sess.query(Gamers).count()):
    ttt_bests_prev.append(sess.query(Gamers).filter_by(id=i+1).first().username)
    snake_bests_prev.append(sess.query(Gamers).filter_by(id=i+1).first().username)

@app.route('/')
def index():
	session.clear()
	session["user_id"] = None
	return redirect(url_for("games"))
	
@app.route('/games')
def games():
	if session["user_id"]:
		return render_template("index.html", name=sess.query(Gamers).filter_by(id=session["user_id"]).first().username)
	else:
		return render_template("index.html", name=0)
	
@app.route('/snake')
def snake():
	return render_template('snake.html')
	
@app.route('/tictactoe')
def tictactoe():
    if session["user_id"]:
        return render_template("tictactoe.html", name=sess.query(Gamers).filter_by(id=session["user_id"]).first().username)
    else:
        return render_template("tictactoe.html", name=0)
    
@app.route('/logout')
def logout():
	session["user_id"] = None
	return redirect(url_for("index"))
	
@app.route('/login', methods=["POST", "GET"])
def login():
	if request.method == "POST":
		gamer_username = request.form.get("Username")
		gamer_hash = request.form.get("Pass").encode()
		print(gamer_username, gamer_hash)
		lookup = sess.query(Gamers).filter_by(username=gamer_username).first()
		print(lookup.username, lookup.hash)
		if not lookup or lookup.hash != hashlib.md5(gamer_hash).hexdigest():
			return("Failure")
		session["user_id"] = lookup.id
		return redirect(url_for("games"))
	else:
		return render_template("login.html")
	
@app.route('/register', methods=["POST", "GET"])
def register():
	if request.method == "POST":
		gamer = Gamers(username=request.form.get("Username"), hash=hashlib.md5(request.form.get("Pass").encode()).hexdigest(), mail=request.form.get("mail"))
		sess.add(gamer)
		sess.commit()
		session["user_id"] = gamer.id
		return redirect(url_for("games"))
	else:
		return render_template('register.html')

@app.route('/records')
@login_required
def records():
    return render_template('records.html', ttt_best = ttt_best, snake_best = snake_best, ttt_users = ttt_bests, snake_users = snake_bests)

@app.route('/results', methods=["POST"])
def results():
    global ttt_best, snake_best, ttt_bests, snake_bests, ttt_bests_prev, snake_bests_prev
    if request.form.get("from")=="tictactoe":
        gamer = sess.query(Gamers).filter_by(id=session["user_id"]).first()
        gamer.ttt += 1
        sess.commit()
        ttt_all = []
        for i in range(sess.query(Gamers).count()):
            ttt_all.append(sess.query(Gamers).filter_by(id=i+1).first().ttt)
        ttt_best = max(ttt_all)
        ttt_bests = []
        for j in range(sess.query(Gamers).count()):
            if ttt_all[j] == ttt_best:
                ttt_bests.append(sess.query(Gamers).filter_by(id=j+1).first().username)
        for user in ttt_bests_prev:
            if user not in ttt_bests:
                msg = MIMEMultipart()
                msg['Subject'] = 'Oh no!'
                msg['From'] = "dembanakh01@gmail.com"
                msg['To'] = sess.query(Gamers).filter_by(username=user).first().mail
                msg.attach(MIMEText("Your record in Tic-Tac-Toe has been broken! Try and defeat your opponent!", "plain"))
                server.sendmail(msg["From"], msg["To"], msg.as_string())
        ttt_bests_prev = ttt_bests
        
    elif request.form.get("from")=="snake":
        gamer = sess.query(Gamers).filter_by(id=session["user_id"]).first()
        gamer.snake = request.form.get("res")
        sess.commit()
        snake_all = []
        for i in range(sess.query(Gamers).count()):
            snake_all.append(sess.query(Gamers).filter_by(id=i+1).first().snake)
        snake_best = max(snake_all)
        snake_bests = []
        for j in range(sess.query(Gamers).count()):
            if snake_all[j] == snake_best:
                snake_bests.append(sess.query(Gamers).filter_by(id=j+1).first().username)
        for user in snake_bests_prev:
            if user not in snake_bests:
                msg = MIMEMultipart()
                msg['Subject'] = 'Oh no!'
                msg['From'] = "dembanakh01@gmail.com"
                msg['To'] = sess.query(Gamers).filter_by(username=user).first().mail
                msg.attach(MIMEText("Your record in Snake has been broken! Try and defeat your opponent!", "plain"))
                server.sendmail(msg["From"], msg["To"], msg.as_string())
        snake_bests_prev = snake_bests
        
    return 'False'

@app.route('/profile')
def profile():
    gamer = sess.query(Gamers).filter_by(id=session["user_id"]).first()
    return render_template('profile.html', name=gamer.username, ttt=gamer.ttt, snake=gamer.snake)

@app.route('/settings')
def settings():
    gamer = sess.query(Gamers).filter_by(id=session["user_id"]).first()
    return render_template('settings.html', name=gamer.username)

@app.route('/change_pas', methods=["POST"])
def change_pas():
    gamer = sess.query(Gamers).filter_by(id=session["user_id"]).first()
    
