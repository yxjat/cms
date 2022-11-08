from datetime import datetime

from cms import db, login_manager,app
# User Mixin  to check if login credentials provide is correct
from flask_login import UserMixin
#
from itsdangerous import TimedJSONWebSignatureSerializer as serial


@login_manager.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))


class user(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20),unique=True,nullable = False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default = 'default.jpeg')
    password = db.Column(db.String(60),nullable=False)
    post = db.relationship('post', backref = 'author', lazy = True)
    course = db.relationship('enrolled', backref = 'member', lazy = True)
    isProf = db.Column(db.Boolean)
    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"

    def get_reset_token(self,expire_sec=1800):
        s = serial(app.config['SECRET_KEY'],expire_sec)
        return s.dumps({'user_id': self.id }).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = serial(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return user.query.get(user_id)
        
        
class post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100),nullable = False)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow )
    content = db.Column(db.Text,nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False)
    credit = db.Column(db.Integer)
    
    def __repr__(self):
        return f"Post('{self.username}','{self.email}','{self.image_file}')"
    
class enrolled(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String(100),nullable = False)
    user_id = db.Column(db.String(100),db.ForeignKey('user.username'),nullable = False)
    course = db.Column(db.String(100),nullable =False)
    teach = db.Column(db.String(100), nullable = False)
    credit = db.Column(db.Integer,nullable = False)

class greviences(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String(100),nullable = False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    content = db.Column(db.String(2000),nullable = False)
