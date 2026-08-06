from models.student import db


class Complaint(db.Model):

    __tablename__ = "complaints"

    id = db.Column(db.Integer, primary_key=True)

    student_name = db.Column(
        db.String(100),
        nullable=False
    )

    room_number = db.Column(
        db.String(20),
        nullable=False
    )

    complaint = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    def __repr__(self):
        return f"<Complaint {self.id}>"