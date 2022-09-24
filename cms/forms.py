from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError
import email_validator
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from cms.model import user

class regform(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min = 2, max = 20) ])

    email = StringField('Email',  validators =[DataRequired(),Email() ])
    password = PasswordField('Password', validators=[DataRequired()])
    confpassword = PasswordField('ConfPassword', validators=[DataRequired(), EqualTo('password')])
    isProf = BooleanField('Check for course instructors')
    submit = SubmitField('Sign Up')
    
    
    
    def validate_username(self,username):
        us = user.query.filter_by(username= username.data).first()
        if us:
            raise ValidationError('This username is taken.Please choose another one')
        
        
    def validate_email(self,email):
        us = user.query.filter_by(email= email.data).first()
        
        if us:
            raise ValidationError('This email is already registered.')

class loginform(FlaskForm):
    
    email = StringField('Email or Username',  validators =[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    
    remember = BooleanField('Remeber Me')

    submit = SubmitField('Login')

class updateprof(FlaskForm):
    
    username = StringField('Username', validators= [DataRequired(), Length(min=2,max=20)])
    email = StringField('Email',  validators =[DataRequired(),Email() ])
    picture = FileField('Update Profile Picture', validators = [FileAllowed(['jpg','png','jpeg'])])
    submit = SubmitField('Update')
    repp = SubmitField('Remove Profile Picture')
    
    def validate_username(self,username):
        if username.data!=current_user.username:
            us = user.query.filter_by(username= username.data).first()
            if us:
                raise ValidationError('This username is taken.Please choose another one')
        
    def validate_email(self,email):
        if email.data!=current_user.email:
            us = user.query.filter_by(email= email.data).first()
            if us:
                raise ValidationError('This email is already registered.')
            
class post_form(FlaskForm):
    
    title = StringField('Title', validators= [DataRequired()])
    
    content = TextAreaField('Content', validators = [DataRequired()])
    
    credit = StringField('Credit' , validators = [DataRequired()])
    
    submit = SubmitField('Post')

class conformation_form(FlaskForm):
    
    confirm = BooleanField('Are you sure you wish to delete this post? This action cannot be undone')
    
    submit = SubmitField('Delete')

class request_reset_form(FlaskForm):
    
    email = StringField('Email',  validators =[DataRequired(),Email() ])
    
    submit = SubmitField('Request Password Reset')
    
    def validate_email(self,email):
        us = user.query.filter_by(email= email.data).first()
        
        if us is None:
            raise ValidationError('This email is not registered.')
        
class password_reset(FlaskForm):
    
    password = PasswordField('Password', validators=[DataRequired()])
    confpassword = PasswordField('ConfPassword', validators=[DataRequired(), EqualTo('password')])
    
    submit = SubmitField('Reset Password')
    
class enrollment_form(FlaskForm):
    #course_id = StringField('Course Id', validators = [DataRequired()])
    name = StringField('Enter your name', validators = [DataRequired()])
    submit = SubmitField('Enrol')
    
class contactForm(FlaskForm):
    name = StringField('Enter your name', validators = [DataRequired()])
    email = StringField('Enter your email address', validators = [DataRequired(),Email()])
    content = TextAreaField('Your Message', validators = [DataRequired()])
    submit = SubmitField('Submit')
    
    
    
        
