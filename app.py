from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import exc
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from email_form_notificator import EmailNotification
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm, ContactForm
from functools import wraps
from flask_gravatar import Gravatar
import os
from dotenv import load_dotenv


#   =======================================
#           CONFIGURE FLASK APP
#   =======================================

"""
    DEFAULT FLASK APP CONFIGURATION
    ===============================
    default_config = {
        'APPLICATION_ROOT': '/',
        'DEBUG': None,
        'ENV': None,
        'EXPLAIN_TEMPLATE_LOADING': False,
        'JSONIFY_MIMETYPE': 'application/json',
        'JSONIFY_PRETTYPRINT_REGULAR': False,
        'JSON_AS_ASCII': True,
        'JSON_SORT_KEYS': True,
        'MAX_CONTENT_LENGTH': None,
        'MAX_COOKIE_SIZE': 4093,
        'PERMANENT_SESSION_LIFETIME': datetime.timedelta(days = 31),
        'PREFERRED_URL_SCHEME': 'http',
        'PRESERVE_CONTEXT_ON_EXCEPTION': None,
        'PROPAGATE_EXCEPTIONS': None,
        'SECRET_KEY': None,
        'SEND_FILE_MAX_AGE_DEFAULT': None,
        'SERVER_NAME': None,
        'SESSION_COOKIE_DOMAIN': None,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_NAME': 'session',
        'SESSION_COOKIE_PATH': None,
        'SESSION_COOKIE_SAMESITE': None,
        'SESSION_COOKIE_SECURE': False,
        'SESSION_REFRESH_EACH_REQUEST': True,
        'TEMPLATES_AUTO_RELOAD': None,
        'TESTING': False,
        'TRAP_BAD_REQUEST_ERRORS': None,
        'TRAP_HTTP_EXCEPTIONS': False,
        'USE_X_SENDFILE': False
    }
"""


# Initial setup for local development
# API_KEY = 'j2312j3knkJBDsadKFJSABFKJ'
# DB_URL = 'sqlite:///blog.db'

# Check if running on local machine or cloud server
is_local = os.environ.get('ENVIRONMENT') is None

if is_local:
    # Load environment variables from .env file
    basedir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(basedir, '.env'))
    API_KEY = os.environ.get("API_KEY")
    DB_URL = os.environ.get("DATABASE_URL")
else:
    # Assume environment variables are already set for cloud server providers
    API_KEY = os.environ.get("API_KEY")
    DB_URL = os.environ.get("DATABASE_URL")

print(DB_URL)

load_dotenv()

app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
ckeditor = CKEditor(app)
Bootstrap(app)

# Flask Debug-toolbar
# https://github.com/flask-debugtoolbar/flask-debugtoolbar
# https://flask-debugtoolbar.readthedocs.io/en/latest/
from flask_debugtoolbar import DebugToolbarExtension
app.debug = True
# toolbar = DebugToolbarExtension(app)

# Procfile configuration:
# // Tell Heroku to:
# //    Create a web worker - one that is able to receive HTTP requests
# //    To use gunicorn to serve your web app
# //    The Flask app object is the app.py file
# web: gunicorn app:app

#   =======================================
#              CONNECT TO DB
#   =======================================

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#   =======================================
#              FLASK LOGIN
#   =======================================

# https://flask-login.readthedocs.io/en/latest/
# YouTube video: https://www.youtube.com/watch?v=2dEM-s3mRLE
# Example: https://gist.github.com/bkdinoop/6698956
login_manager = LoginManager()  # Instantiate the Flask Login extension

# Specify the default login URL in the Flask-Login
# login_manager.login_view = 'login'
# login_manager.login_message = u"Please log in to access this page."
# login_manager.setup_app(app)

login_manager.init_app(app)  # Initialise the manager passing the app to it

#   =======================================
#             GRAVATAR AVATARS
#   =======================================

gravatar = Gravatar(
    app,
    size=100,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None
)


#   =======================================
#              CONFIGURE TABLES
#   =======================================

class User(UserMixin, db.Model):
    # A user can have many blog posts, but a post can only belong to one user.
    # This is a one-to-many relationship.
    # User is the PARENT, BlogPost is the CHILD.
    # https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html
    # https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
    # https://www.youtube.com/watch?v=juPQ04_twtA

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    # https://www.reddit.com/r/flask/comments/142gqe/trying_to_understand_relationships_in_sqlalchemy/
    # The "posts" attribute for the User object is a list.
    # This list defines the relationship and it can be empty or contain zero or many objects.
    # To add a post to a user you'll define a user object, a post object and append the post object to user.posts.
    # The back_populates allows you to get the user object from a post object (post.user).
    # With back_populates, both sides of the relationship are defined explicitly

    # Create reference to the BlogPost class - "author" refers to the author property in the BlogPost class
    # posts is a "pseudo column" in this "users" table
    # For example, you could use user.posts to retrieve the list of posts that user has created
    posts = db.relationship('BlogPost', back_populates='author')  # refers to the child
    # Create reference to the Comments class - "commenter" refers to the commenter property in the Comments class
    # comments is a "psuedo column" in this "users" table
    # For example, you could use user.comments to retrieve the list of comments that user has created
    comments = db.relationship('Comment', back_populates='commenter')  # refers to the child

    # Method to set the password hash
    def set_password(self, input_password):
        self.password = generate_password_hash(input_password)

    # Method to check the password hash
    def check_password(self, input_password):
        return check_password_hash(self.password, input_password)


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # Create ForeignKey "users.id" - refers to the tablename of User class
    # ForeignKey refers to the primary key in the other *table* (users)
    # author_id is a real column in this "blog_posts" table
    # Without the ForeignKey, the relationships would not work.
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Create reference to the User class - "posts" refers to the posts property in the User class
    # author is a "pseudo column" in this "blog_posts" table
    # For example, you could use blog_post.author to retrieve the user who created the post
    author = db.relationship('User', back_populates='posts')  # refers to the parent
    # Create reference to the Comment class - "post" refers to the post property in the Comment class
    # comments is a "pseudo column" in this "blog_post" table
    # For example, you could use blog_post.comments to retrieve the list of comments related to that post
    comments = db.relationship('Comment', back_populates='post')  # refers to the child


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)

    # Create ForeignKey "blog_posts.id" - refers to the tablename of BlogPost class
    # ForeignKey refers to the primary key in the other *table* (blog_posts)
    # post_id is a real column in this "comments" table
    # Without the ForeignKey, the relationships would not work.
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    # Create reference to the BlogPost class - "comments" refers to the comments property in the BlogPost class
    # post is a "pseudo column" in this "blog_posts" table
    # For example, you could use comment.post to retrieve the post associated with this comment
    post = db.relationship('BlogPost', back_populates='comments')  # refers to the parent
    # Create ForeignKey "user.id" - refers to the tablename of User class
    # ForeignKey refers to the primary key in the other *table* (users)
    # commenter_id is a real column in this "comments" table
    # Without the ForeignKey, the relationships would not work.
    commenter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Create reference to the User class - "comments" refers to the comments property in the User class
    # commenter is a "pseudo column" in this "comments" table
    # For example, you could use comment.commenter to retrieve the user associated with this comment
    commenter = db.relationship('User', back_populates='comments')  # refers to the parent


# Create the database file if it doesn't exist - also used to create / modify tables
if not os.path.isfile('sqlite:///blog.db'):
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    """
    This callback is used to reload the user object from the user ID stored in the session.
    It connects the abstract user that Flask Login uses with the actual users in the model
    It should take the unicode ID of a user, and return the corresponding user object.
    It should return None (not raise an exception) if the ID is not valid.
    (In that case, the ID will manually be removed from the session and processing will continue.)
    :param user_id: unicode user ID
    :return: user object
    """
    return User.query.get(int(user_id))


def admin_only(f):
    # A decorator is a function that wraps and replaces another function.
    # Since the original function is replaced, you need to remember to copy
    # the original function’s information to the new function.
    # Use functools.wraps() to handle this for you.
    # https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/#login-required-decorator
    # https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If user is not logged in or id is not 1 then return abort with 403 error
        if current_user.is_anonymous or current_user.id != 1:
            return abort(403)  # Forbidden
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


# def authorised_only(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         #If id is not authorised then return abort with 403 error
#         if current_user.is_anonymous:
#             return abort(403)
#         #Otherwise continue with the route function
#         return f(*args, **kwargs)
#     return decorated_function


#   =======================================
#               ERROR HANDLER
#   =======================================

@app.errorhandler(403)
def forbidden(e):
    print(e)
    return render_template('403.html', error=e), 403


@app.errorhandler(404)
def forbidden(e):
    print(e)
    return render_template('404.html', error=e), 404


#   =======================================
#                  ROUTES
#   =======================================


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route("/about")
def about():
    return render_template("about.html")


# Define a route for the "/contact" URL that supports both GET and POST requests
@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    # if request.method == "POST":
    if form.validate_on_submit():
        print('yes')
        data = form.data
        print(data['email'], data["name"], data["phone"], data["message"])
        mail = EmailNotification(recipient=data['email'],
                                 name=data["name"],
                                 phone=data["phone"],
                                 customer_message=data["message"])
        mail.send_email()
        flash(f"Message's been sent successfully!", 'info')
        return redirect(url_for("contact"))
    return render_template("contact.html", form=form)


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    list_comments = requested_post.comments
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You cannot comment.\nYou are not logged in.", category="error")
            return redirect(url_for("login"))
        print(requested_post, current_user)
        new_comment = Comment(
            text=form.comment_text.data,
            post=requested_post,
            commenter=current_user,
            date=date.today().strftime("%d/%b/%Y")
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))
    return render_template("post.html", post=requested_post, form=form, comments=list_comments)


# The delete_post function deletes a blog post from the database and redirects to the home page.
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


# The add_new_post function is a route that handles creating a new blog post. If the form is submitted and validated,
# a new BlogPost object is created and added to the database.
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        flash("Your post's successfully published")
        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form)


# The edit_post function is a route that handles editing an existing blog post. If the form is submitted and validated,
# the changes are applied to the corresponding BlogPost object and saved in the database.
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        # author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        # because the request is coming from a HTML form, you should accept the edited post as a POST request.
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        # post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()  # WTF form for the web page
    user = User()  # Create a new user object
    # Pass all the form attributes over to a new user object (names of attributes must be mathced)
    form.populate_obj(user)
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first() is not None:
            flash(f"User {user.email} already exists!", 'info')
            return redirect(url_for("register"))
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        print(f'Registered new user: {user.name}')
        flash("Registration successful")
        login_user(user)
        flash('Login successful.', 'info')
        return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # Make sure the user exists
        try:
            user = User.query.filter_by(email=email).first()
        except exc.NoResultFound:
            # SQLAlchemy.orm exception
            flash(f"User {email} not found!", 'error')
            flash(f"Try again.")
            print(f"SQLAlchemy.orm exception: User {email} not found!")
            return render_template("login.html", form=form)
        if user:
            # Check the hashed password in the database against the input password
            if user.check_password(input_password=password):
                # Log in and authenticate the user
                login_user(user)

                # Flash Messages will show on the page that is redirected to (redirect only, not render_template)
                # as long as the HTML is coded of course.
                # See flash.html which is included in other html pages: {% include 'flash.html' %}
                #   optional category: 'message', 'info', 'warning'. 'error'
                flash('Login successful.', 'info')

                # Warning: You MUST validate the value of the next parameter.
                # If you do not, your application will be vulnerable to open redirects.
                #   Example: A logged out user enters the URL: http://127.0.0.1:5008/secrets
                #   /secrets is protected, so the user is redirected to the login page:
                #   http://127.0.0.1:5008/login?next=%2Fsecrets
                #   Once the user has logged in, we redirect to where they wanted to go using the "next" attribute
                # TODO: Handle the "next" parameter

                print(f'Login: user.name = {user.name}')

                return redirect(url_for('get_all_posts'))
            else:
                flash(f'Incorrect Password for {email}', 'error')
                flash(f"Try again.")
                return render_template("login.html", form=form)
        else:  # User == None
            flash(f"User {email} not found!", 'error')
            flash(f"Try again.")
            return render_template("login.html", form=form)
    return render_template("login.html", form=form)


# When applying further decorators, always remember that the route() decorator is always the outermost.
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


#   =======================================
#               IF A PORT IN USE
#   =======================================
# To kill a particular PID associated with a process running on port 5000,
# you can use the kill command along with the PID number. Here are the steps you can follow:
# Run the following command to find the PID associated with the process running on port 5000:
# lsof -i tcp:5000
# This will list all the processes running on port 5000 along with their respective PIDs.
# Find the PID of the Python process you want to kill from the output of the previous command.
# Use the kill command to terminate the process. For example, if the PID is 1234, you can run the following command:
# kill 1234
# This will send a SIGTERM signal to the process, which will allow it to perform cleanup operations before terminating.
# If the process does not terminate within a reasonable amount of time, you can use the kill -9 command to send a SIGKILL signal, which will immediately terminate the process:
# kill -9 1234

# e.g.

# COMMAND     PID          USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
# ControlCe 18752 maksimkisliak    7u  IPv4 0xa1c716e4639e3559      0t0  TCP *:commplex-main (LISTEN)
# ControlCe 18752 maksimkisliak    8u  IPv6 0xa1c716e4613d3371      0t0  TCP *:commplex-main (LISTEN)

# kill -9 18752

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
