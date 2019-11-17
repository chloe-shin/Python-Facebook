from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

#default coder for flask_login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'
app.secret_key = 'abc'

#create database model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(10), nullable=False, unique=False)

    #password: 지금 입력한 비밀번호 #self.password: 사용자 비밀번호
    def generate_password(self, password):
        self.password = generate_password_hash(password) #password를 암호화

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String(20), nullable=False)
    body = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def comments(self):
        return Comments.query.filter_by(post_id = self.id).all()

class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

#create table based on the model that I created
db.create_all()

#flask_login > login_manager default code
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

#set route / link home page
@app.route('/', methods = ["GET"])
@login_required 
def root():   
    # query posts from database
    posts = Post.query.order_by(Post.created.desc()).all()
    # modify our posts so that each post will include all author info:
    for post in posts:
      post.author = User.query.filter_by(id=post.user_id).first()
    return render_template("home.html", posts=posts)

#set route / link creating post
@app.route('/posts', methods=['POST'])
@login_required
def create_post():
    if request.method=='POST':
        new_post = Post(body=request.form['body'],
                        user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
    return redirect(url_for('root'))


@app.route('/posts/<id>', methods=['POST', 'GET'])
def single_post(id):
    action = request.args.get('action')
    print('asdasdasdsadsads', request.args.get("charles"))
    post = Post.query.get(id)
    if not post:
        flast('Post not found', 'warning')
        return redirect(url_for('root'))
    post.author = User.query.get(post.user_id)
    if request.method=="POST":
        if post.user_id != current_user.id:
            flash('not allowed to post', 'danger')
            return redirect(url_for('root'))
        if action == 'delete':
            db.session.delete(post)
            db.session.commit()
            return redirect(url_for('root'))
        elif action == 'update':
            post.body = request.form['body']
            db.session.commit()
            return redirect(url_for('single_post', id=id))
        elif action == 'edit':
            return render_template('single_post.html', post = post, action = action  )
    if not action:
        action = 'view'
    return render_template('single_post.html', post = post, action= action)


@app.route('/post/<post_id>/comments', methods = ["POST"])
def create_comment(post_id):
    new_comment = Comments(body = request.form["body"],
                          user_id = current_user.id,
                          post_id = post_id )
    # comments = Comment.query.get(post.id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('root')) 

@app.route('/comments/<id>/delete', methods = ["POST"])
def delete_comment(id):
    comment = Comments.query.get(id)
    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for('root'))

#set route / link register page
@app.route('/register', methods = ["GET", "POST"])
def register():
    #logic here
    if current_user.is_authenticated:
      return redirect(url_for('root'))
    # If the user submit the form, this line will be checked
    if request.method == 'POST':
        # Use email user provides / check if that email is taken or not
        check_email = User.query.filter_by(email=request.form['email']).first() 
        if check_email:  #if email taken
            flash('Email already taken', 'warning') # we alert the user
            return redirect(url_for('register')) # then reload the register page again
        
        # if email not taken, we add new user to the database
        # set new_user as below:
        # = User class take data as below:
        new_user = User(username=request.form['username'],
                        email=request.form['email'])
        #raw password will be hashed using the generate_password method
        new_user.generate_password(request.form['password'])
        db.session.add(new_user) # then we add new user to our session
        db.session.commit() # then we commit to our database (kind of like save to db)
        login_user(new_user) # then we log this user into our system
        flash('Successfully create an account and logged in', 'success')
        # and redirect user to our root which reder to home.html
        return redirect(url_for('root')) 

    # By default (GET REQUEST), python will skip this condition... 
    # ...and just return render_template at the end of this function. 
    return render_template("register.html")


#set route / link login page
@app.route('/login', methods = ["GET", "POST"])
def login():
    #logic here
    if current_user.is_authenticated:
      return redirect(url_for('root'))
    if request.method == 'POST':
        #check if the email that user provides exsist?
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
    

#logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



#default code to run server in flask
if __name__ == "__main__":
    app.run(debug=True)