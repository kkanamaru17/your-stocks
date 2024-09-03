from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(150), unique=True, nullable=False)
#     password = db.Column(db.String(150), nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    latest_price = db.Column(db.Float, nullable=True)
    return_performance = db.Column(db.Float, nullable=True, default=0.0)
    forward_pe = db.Column(db.Float, nullable=True, default=0.0)
    div_yield = db.Column(db.Float, nullable=True, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)