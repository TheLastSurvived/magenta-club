from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.Integer)
    password = db.Column(db.String(100), unique=True)
    root = db.Column(db.Integer, default=0)
    orders = db.relationship('Orders', backref='user', lazy=True)


    def __repr__(self):
        return 'User %r' % self.id 


class News(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.now)
    category = db.Column(db.String(100))
    text = db.Column(db.Text)
    image = db.Column(db.LargeBinary)
    image_name = db.Column(db.String(100))

    def __repr__(self):
        return 'News %r' % self.id 


class Service(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title_service = db.Column(db.String(100))
    common = db.Column(db.Integer)
    vip = db.Column(db.Integer)
    bootcamp = db.Column(db.Integer)

    def __repr__(self):
        return 'Service %r' % self.id 

class Orders(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    price = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.now)
    service_name = db.Column(db.String(100))
    service_type = db.Column(db.String(100))
    qr_image = db.Column(db.LargeBinary)
    qr_image_name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return 'Orders %r' % self.id


