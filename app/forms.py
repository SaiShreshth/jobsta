from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, EmailField, PasswordField, URLField, DateTimeField, RadioField
from wtforms.validators import DataRequired, Email, Length, Regexp, URL, Optional
from datetime import datetime

class JobForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    company = StringField('Company', validators=[DataRequired()])
    location = StringField('Location')
    salary = StringField('Salary')
    apply_url = URLField('Apply URL', validators=[DataRequired(), URL()])
    application_email = EmailField('Application Email (optional)', validators=[Optional(), Email()])
    deadline = DateTimeField('Deadline (Optional)', validators=[Optional()], format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Create Job')

class EditJobForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    company = StringField('Company', validators=[DataRequired()])
    location = StringField('Location')
    salary = StringField('Salary')
    apply_url = URLField('Apply URL', validators=[DataRequired(), URL()])
    application_email = EmailField('Application Email (optional)', validators=[Optional(), Email()])
    deadline = DateTimeField('Deadline (Optional)', validators=[Optional()], format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Update Job')

class DeleteJobForm(FlaskForm):
    action = RadioField('Action', choices=[
        ('delete', 'Delete (Permanently remove job and applications)'),
        ('mark_as_deleted', 'Mark as Deleted (Keep data, notify applicants)'),
        ('archive', 'Archive (Keep data, notify applicants)')
    ], validators=[DataRequired()], default='mark_as_deleted')
    submit = SubmitField('Confirm Action')

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

class RecommendationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    body = TextAreaField('Recommendation', validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Submit')