from flask import Blueprint, request, url_for, render_template, redirect, flash
from src.models import Post, User, Comments
from src import db
from flask_login import login_required, current_user



posts_blueprint = Blueprint('posts', __name__, template_folder="../../templates", static_folder="./static")




# set route / link creating post
@posts_blueprint.route('/', methods=['POST'])
@login_required
def create_post():
    if request.method == 'POST':
        new_post = Post(body=request.form['body'],
                        user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
    return redirect(url_for('root'))


@posts_blueprint.route('/<id>', methods=['POST', 'GET'])
def single_post(id):
    action = request.args.get('action')
    post = Post.query.get(id)
    if not post:
        flash('Post not found', 'warning')
        return redirect(url_for('root'))
    post.author = User.query.get(post.user_id)
    if request.method == "POST":
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
            return redirect(url_for('posts.single_post', id=id))
        elif action == 'edit':
            return render_template('single_post.html', post=post, action=action)
        ## like
        elif action == 'like':
            post.like_time = post.like_time + 1
            print(post.like_time,'like_time')
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('root'))
    if not action:
        action = 'view'
    return render_template('single_post.html', post=post, action=action)


@posts_blueprint.route('/<post_id>/comments', methods=["POST"])
def create_comment(post_id):
    new_comment = Comments(body=request.form["body"],
                           user_id=current_user.id,
                           post_id=post_id)
    # comments = Comment.query.get(post.id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('root'))


@posts_blueprint.route('/comments/<id>/delete', methods=["POST"])
def delete_comment(id):
    comment = Comments.query.get(id)
    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for('root'))
