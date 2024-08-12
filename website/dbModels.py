from . import db
from flask_login import UserMixin

students_course=db.Table("students course",
                        db.Column(db.Integer,db.ForeignKey("students.id",ondelete="CASCADE"),name="students_id"),
                        db.Column(db.Integer,db.ForeignKey("course.id",ondelete="CASCADE"),name="course_id")
                         )

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(150),nullable=False)
    email=db.Column(db.String)
    role=db.Column(db.String,nullable=False)
    course=db.Column(db.String,nullable=False)
    password=db.Column(db.String)

class Students(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    std_id=db.Column(db.BigInteger, nullable=False)
    firstname=db.Column(db.String(50), nullable=False)
    lastname=db.Column(db.String(50), nullable=False)
    dob=db.Column(db.String, nullable=False)
    gender=db.Column(db.String, nullable=False)
    pob=db.Column(db.String, nullable=False)
    nationality=db.Column(db.String(50), nullable=False)
    admisision_date=db.Column(db.String, nullable=False)
    current_track=db.Column(db.String, nullable=False)
    offers=db.relationship("Course",secondary=students_course,backref="students",passive_deletes=True)

class Course(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100), nullable=False)
    credit=db.Column(db.Integer)
    marks=db.relationship("Marks",backref="course",passive_deletes=True)

class Marks(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    level=db.Column(db.String)
    semister=db.Column(db.String)
    mid=db.Column(db.Integer,default=0)
    exam=db.Column(db.Integer,default=0)
    total=db.Column(db.Integer,default=0)
    grade=db.Column(db.String(5),default="None")
    course_id=db.Column(db.Integer,db.ForeignKey("course.id",ondelete="CASCADE"))
    student_id=db.Column(db.Integer,db.ForeignKey("students.id",ondelete="CASCADE"))