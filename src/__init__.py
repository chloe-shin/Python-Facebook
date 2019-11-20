from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, login_required, logout_user
from flask_migrate import Migrate
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_folder="static")
app.config.from_object('config.Config')



db = SQLAlchemy(app)
from src.models import User, Post

# default coder for flask_login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# flask_login > login_manager default code
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


migrate = Migrate(app, db)

# set route / link home page
@app.route('/', methods=["GET"])
@login_required
def root():
    # query posts from database
    posts = Post.query.order_by(Post.created.desc()).all()
    # modify our posts so that each post will include all author info:
    for post in posts:
        post.author = User.query.filter_by(id=post.user_id).first()
    if filter:
        return render_template("home.html", posts=posts)


from src.components.post import posts_blueprint
app.register_blueprint(posts_blueprint, url_prefix='/posts')



# set route / link register page
@app.route('/register', methods=["GET", "POST"])
def register():
    # logic here
    if current_user.is_authenticated:
        return redirect(url_for('root'))
    # If the user submit the form, this line will be checked
    if request.method == 'POST':
        # Use email user provides / check if that email is taken or not
        check_email = User.query.filter_by(email=request.form['email']).first()
        if check_email:  # if email taken
            flash('Email already taken', 'warning')  # we alert the user
            return redirect(url_for('register'))  # then reload the register page again

        # if email not taken, we add new user to the database
        # set new_user as below:
        # = User class take data as below:
        new_user = User(username=request.form['username'],
                        email=request.form['email'])
        # raw password will be hashed using the generate_password method
        new_user.generate_password(request.form['password'])
        db.session.add(new_user)  # then we add new user to our session
        db.session.commit()  # then we commit to our database (kind of like save to db)
        login_user(new_user)  # then we log this user into our system
        flash('Successfully create an account and logged in', 'success')
        # and redirect user to our root which reder to home.html
        return redirect(url_for('root'))

        # By default (GET REQUEST), python will skip this condition...
    # ...and just return render_template at the end of this function. 
    return render_template("register.html")


# set route / link login page
@app.route('/login', methods=["GET", "POST"])
def login():
    # logic here
    if current_user.is_authenticated:
        return redirect(url_for('root'))
    if request.method == 'POST':
        # check if the email that user provides exsist?
        user = User.query.filter_by(email=request.form['email']).first()
        if not user:
            flash('Email is not registered', 'warning')
            return redirect(url_for('register'))
        if user.check_password(request.form['password']):
            login_user(user)
            flash(f'Welcome back {current_user.username}', 'success')
            # flash('Welcome back {}'.format(current_user.name), 'success')
            return redirect(url_for('root'))
        flash('Wrong password', 'warning')
        return redirect(url_for('login'))
    return render_template("login.html")

@app.route('/user/<int:user_id>')
def Profile(user_id):
    posts = Post.query.filter(Post.user_id == user_id).all()
    # modify our posts so that each post will include all author info:
    for post in posts:
        post.author = User.query.filter_by(id=post.user_id).first()
    return render_template("profile.html", posts=posts[::-1])

@app.route('/post/<int:post_id>')
def Posts(post_id):
    post = Post.query.filter(Post.id == post_id).first()
    post.author = User.query.filter_by(id=post.user_id).first()
    return render_template("post.html", post=post)



# logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


