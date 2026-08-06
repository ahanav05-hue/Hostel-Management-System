from models.student import db


class Room(db.Model):

    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)

    room_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    capacity = db.Column(
        db.Integer,
        nullable=False
    )

    occupied = db.Column(
        db.Integer,
        default=0
    )

    status = db.Column(
        db.String(20),
        default="Available"
    )

    def __repr__(self):
        return f"<Room {self.room_number}>"