from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, URL, Email, Length, Regexp
# https://wtforms.readthedocs.io/en/2.3.x/validators/#module-wtforms.validators
# Email() requires WTForms email_validator package:
#       pip install wtforms[email]
from flask_ckeditor import CKEditorField


# The CreatePostForm class is a Flask-WTF form that is used to create or edit a blog post, with fields for the title,
# subtitle, image URL, body, and a submit button.
class CreatePostForm(FlaskForm):
    title = StringField(
        label="Blog Post Title",
        validators=[DataRequired()]
    )
    subtitle = StringField(
        label="Subtitle",
        validators=[DataRequired()]
    )
    img_url = StringField(
        label="Blog Image URL",
        validators=[DataRequired(), URL()]
    )
    body = CKEditorField(
        label="Blog Content",
        validators=[DataRequired()]
    )
    submit = SubmitField(
        label="Submit Post"
    )


class RegisterForm(FlaskForm):
    email = StringField(
        label="Email",
        validators=[DataRequired(), Email(check_deliverability=True)],
        render_kw={'style': 'width: 60ch'}
    )
    password = PasswordField(
        label="Password",
        validators=[DataRequired(), Length(min=6)],
        render_kw={'style': 'width: 60ch'}
    )
    name = StringField(
        label="Name",
        validators=[DataRequired()],
        render_kw={'style': 'width: 60ch'}
    )
    submit = SubmitField(
        label="Sign Me Up",
        render_kw={'btn-dark': 'True'}
    )


class LoginForm(FlaskForm):
    email = StringField(
        label="email",
        validators=[DataRequired(), Email(check_deliverability=True)],
        render_kw={'style': 'width: 60ch'}
    )
    password = PasswordField(
        label="password",
        validators=[DataRequired(), Length(min=6)],
        render_kw={'style': 'width: 60ch'}
    )
    remember_me = BooleanField(label="remember me")
    submit = SubmitField(
        label="log in",
        render_kw={'btn-dark': 'True'}
    )


class CommentForm(FlaskForm):
    comment_text = CKEditorField(
        label="",
    )
    submit = SubmitField(
        label="Comment",
        render_kw={'btn-dark': 'True'}
    )


class ContactForm(FlaskForm):
    name = StringField(
        label="name",
        validators=[DataRequired(), Regexp("^[a-zA-Z ]*$", message="Name should only contain letters and spaces.")],
        render_kw={'style': 'width: 60ch'}
    )
    email = StringField(
        label="email",
        validators=[DataRequired(), Email(check_deliverability=True)],
        render_kw={'style': 'width: 60ch'}
    )
    phone = StringField(
        label="phone",
        validators=[DataRequired(), Length(min=9), Regexp("^[0-9]+$", message="Phone number should only contain numbers.")],
        render_kw={'style': 'width: 60ch'}
    )
    message = StringField(
        label="message",
        validators=[DataRequired(), Length(min=10, max=200, message="Message should be between 10 and 200 characters.")],
        render_kw={'style': 'width: 60ch'}
    )
    submit = SubmitField(
        label="send",
        render_kw={'btn-dark': 'True'}
    )