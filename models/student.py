from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Student(db.Model):

    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    usn = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    branch = db.Column(
        db.String(50),
        nullable=False
    )

    semester = db.Column(
        db.Integer,
        nullable=False
    )

    room_number = db.Column(
        db.String(20),
        nullable=True
    )

    def __repr__(self):
        return f"<Student {self.name}>"