from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Regexp

class JobForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    company = StringField('Company', validators=[DataRequired()])
    location = StringField('Location')
    salary = StringField('Salary')
    submit = SubmitField('Create Job')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password')
    submit = SubmitField('Login')

class SetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(r'.*[a-zA-Z].*', message='Must contain at least one letter'),
        Regexp(r'.*\d.*', message='Must contain at least one number')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Set Password')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(r'.*[a-zA-Z].*', message='Must contain at least one letter'),
        Regexp(r'.*\d.*', message='Must contain at least one number')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')