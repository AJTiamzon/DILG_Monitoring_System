from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')

class Brngy_files4(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.String(10000))
    added_by = db.Column(db.String(10000))
    barang_name = db.Column(db.String(10000))
    road_clearing = db.Column(db.String(10000))
    kp = db.Column(db.String(10000))
    vawc = db.Column(db.String(10000))
    first_time_job_seeking = db.Column(db.String(10000))
    bfdp = db.Column(db.String(10000))
    kasambahay = db.Column(db.String(10000))
    manila_bay_w1 = db.Column(db.String(10000))
    manila_bay_w2 = db.Column(db.String(10000))
    manila_bay_w3 = db.Column(db.String(10000))
    manila_bay_w4 = db.Column(db.String(10000))
    manila_bay_w5 = db.Column(db.String(10000))
    kalinisan_w1 = db.Column(db.String(10000))
    kalinisan_w2 = db.Column(db.String(10000))
    kalinisan_w3 = db.Column(db.String(10000))
    kalinisan_w4 = db.Column(db.String(10000))
    kalinisan_w5 = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    links = db.relationship('SubjectLinks3', backref='barangay', lazy=True)
    
class SubjectLinks3(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.String(10000))
    added_by = db.Column(db.String(10000))
    subject = db.Column(db.String(10000))
    link = db.Column(db.String(10000))

    barangay_id = db.Column(db.Integer, db.ForeignKey('brngy_files4.id'))


class Barangay_Names(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barang_name = db.Column(db.String(10000))


