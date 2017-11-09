from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class User(db.Model):
    User_ID = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    Password = db.Column(db.String(120))
    
    def __init__(self, email, Password):
        self.email = email
        self.Password = Password

    def __repr__(self):
        return '<User %r>' % self.email

class Blogz(db.Model):

    ID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(40))
    MSG = db.Column(db.String(255))
    User_ID = db.Column(db.Integer)

    def __init__(self, Title, MSG, User_ID):
        self.Title = request.form['Title']
        self.MSG = request.form['MSG']
        email = session['user']
        users = User.query.filter_by(email=email)
        if users.count() == 1:
            user = users.first()
            User_ID = user.User_ID
        self.User_ID = User_ID

@app.route('/', methods=['POST', 'GET'])
def index():

    users = User.query.all()
    return render_template('index.html',title="Build-a-Blog!", users = users)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    ID = request.args.get("id")
    User_ID = request.args.get("user_id")
    if ID:
        posts = Blogz.query.filter_by(ID=ID).all()
        return render_template('single.html',title="build-a-Blog!", posts = posts)
    
    elif User_ID:
        posts = Blogz.query.filter_by(User_ID=User_ID).all()
        return render_template('single.html',title ="build-a-blog!", posts = posts)

    else:
        posts = Blogz.query.all()
        return render_template('blogs.html',title="build-a-Blog!", posts = posts)

@app.route('/newpost', methods=['POST', 'GET'])
def form():
    if request.method == 'POST':
        Title_name = request.form['Title']
        MSG_body = request.form['MSG']
        email = session['user']
        users = User.query.filter_by(email=email)
        if users.count() == 1:
            user = users.first()
            User_ID = user.User_ID
        new_post = Blogz(Title_name, MSG_body, User_ID)
        db.session.add(new_post)
        db.session.commit()
    return render_template('newpost.html', title="Build-a-Blog")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.query.filter_by(email=email)
        if users.count() == 1:
            user = users.first()
            if password == user.Password:
                session['user'] = user.email
                flash('welcome back, '+user.email)
                return redirect("/")
        flash('bad username or password')
        return redirect("/login")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not is_email(email):
            flash('zoiks! "' + email + '" does not seem like an email address')
            return redirect('/register')
        email_db_count = User.query.filter_by(email=email).count()
        if email_db_count > 0:
            flash('yikes! "' + email + '" is already taken and password reminders are not implemented')
            return redirect('/register')
        if password != verify:
            flash('passwords did not match')
            return redirect('/register')
        user = User(email=email, Password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.email
        return redirect("/blog")
    else:
        return render_template('register.html')
    
def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

@app.route("/logout", methods=['GET','POST'])
def logout():
    if request.method =='POST':
        del session['user']
        return redirect("/")
    else:
        return render_template('logout.html')

endpoints_without_login = ['login', 'register']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/register")


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == "__main__":
    app.run()
