from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_file
)

from config import Config

from models.student import db, Student
from models.room import Room
from models.complaint import Complaint

import io
import csv

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle
)

from reportlab.lib import colors

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


# ===========================================================
# DASHBOARD
# ===========================================================

@app.route("/")
@app.route("/dashboard")
def dashboard():

    search = request.args.get("search", "")

    query = Student.query

    if search:

        query = query.filter(

            (Student.name.contains(search))

            |

            (Student.usn.contains(search))

        )

    students = query.order_by(
        Student.id.desc()
    ).all()

    total_students = Student.query.count()

    total_rooms = Room.query.count()

    occupied_rooms = db.session.query(
        Student.room_number
    ).filter(
        Student.room_number.isnot(None),
        Student.room_number != ""
    ).distinct().count()

    available_rooms = max(
        total_rooms - occupied_rooms,
        0
    )

    pending_complaints = Complaint.query.filter_by(
        status="Pending"
    ).count()

    return render_template(

        "dashboard.html",

        students=students,

        search=search,

        total_students=total_students,

        total_rooms=total_rooms,

        occupied_rooms=occupied_rooms,

        available_rooms=available_rooms,

        pending_complaints=pending_complaints

    )


# ===========================================================
# ADD STUDENT
# ===========================================================

@app.route("/student/add", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        room_number = request.form["room_number"]

        room = Room.query.filter_by(
            room_number=room_number
        ).first()

        if room:

            if room.occupied >= room.capacity:

                flash(
                    "Selected room is already full.",
                    "danger"
                )

                return redirect(
                    url_for("add_student")
                )

        student = Student(

            usn=request.form["usn"],

            name=request.form["name"],

            email=request.form["email"],

            phone=request.form["phone"],

            branch=request.form["branch"],

            semester=int(
                request.form["semester"]
            ),

            room_number=room_number

        )

        db.session.add(student)

        if room:

            room.occupied += 1

            if room.occupied >= room.capacity:

                room.status = "Occupied"

            else:

                room.status = "Available"

        db.session.commit()

        flash(
            "Student Added Successfully!",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    rooms = Room.query.filter(
        Room.occupied < Room.capacity
    ).all()

    return render_template(

        "add_student.html",

        rooms=rooms

    )
    # ===========================================================
# EDIT STUDENT
# ===========================================================

@app.route("/student/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    student = Student.query.get_or_404(id)

    if request.method == "POST":

        old_room_number = student.room_number
        new_room_number = request.form["room_number"]

        # Room changed
        if old_room_number != new_room_number:

            old_room = Room.query.filter_by(
                room_number=old_room_number
            ).first()

            if old_room:

                old_room.occupied = max(
                    old_room.occupied - 1,
                    0
                )

                if old_room.occupied < old_room.capacity:

                    old_room.status = "Available"

            new_room = Room.query.filter_by(
                room_number=new_room_number
            ).first()

            if new_room:

                if new_room.occupied >= new_room.capacity:

                    flash(
                        "Selected room is already full.",
                        "danger"
                    )

                    return redirect(
                        url_for(
                            "edit_student",
                            id=id
                        )
                    )

                new_room.occupied += 1

                if new_room.occupied >= new_room.capacity:

                    new_room.status = "Occupied"

        student.usn = request.form["usn"]

        student.name = request.form["name"]

        student.email = request.form["email"]

        student.phone = request.form["phone"]

        student.branch = request.form["branch"]

        student.semester = int(
            request.form["semester"]
        )

        student.room_number = new_room_number

        db.session.commit()

        flash(
            "Student Updated Successfully!",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    rooms = Room.query.all()

    return render_template(

        "edit_student.html",

        student=student,

        rooms=rooms

    )


# ===========================================================
# DELETE STUDENT
# ===========================================================

@app.route("/student/delete/<int:id>")
def delete_student(id):

    student = Student.query.get_or_404(id)

    room = Room.query.filter_by(
        room_number=student.room_number
    ).first()

    if room:

        room.occupied = max(
            room.occupied - 1,
            0
        )

        if room.occupied < room.capacity:

            room.status = "Available"

    db.session.delete(student)

    db.session.commit()

    flash(
        "Student Deleted Successfully!",
        "warning"
    )

    return redirect(
        url_for("dashboard")
    )
    # ===========================================================
# ROOM MANAGEMENT
# ===========================================================

@app.route("/rooms", methods=["GET", "POST"])
def rooms():

    if request.method == "POST":

        room_number = request.form["room_number"].strip()

        capacity = int(
            request.form["capacity"]
        )

        existing_room = Room.query.filter_by(
            room_number=room_number
        ).first()

        if existing_room:

            flash(
                "Room already exists.",
                "warning"
            )

            return redirect(
                url_for("rooms")
            )

        room = Room(

            room_number=room_number,

            capacity=capacity,

            occupied=0,

            status="Available"

        )

        db.session.add(room)

        db.session.commit()

        flash(
            "Room Added Successfully!",
            "success"
        )

        return redirect(
            url_for("rooms")
        )

    room_list = Room.query.order_by(
        Room.room_number
    ).all()

    return render_template(

        "rooms.html",

        rooms=room_list

    )


# ===========================================================
# DELETE ROOM
# ===========================================================

@app.route("/room/delete/<int:id>")
def delete_room(id):

    room = Room.query.get_or_404(id)

    students = Student.query.filter_by(
        room_number=room.room_number
    ).count()

    if students > 0:

        flash(
            "Cannot delete a room that has students assigned.",
            "danger"
        )

        return redirect(
            url_for("rooms")
        )

    db.session.delete(room)

    db.session.commit()

    flash(
        "Room Deleted Successfully!",
        "warning"
    )

    return redirect(
        url_for("rooms")
    )


# ===========================================================
# UPDATE ROOM STATUS
# ===========================================================

@app.route("/room/update-status/<int:id>")
def update_room_status(id):

    room = Room.query.get_or_404(id)

    room.occupied = Student.query.filter_by(
        room_number=room.room_number
    ).count()

    if room.occupied >= room.capacity:

        room.status = "Occupied"

    else:

        room.status = "Available"

    db.session.commit()

    flash(
        "Room Status Updated!",
        "success"
    )

    return redirect(
        url_for("rooms")
    )
    # ===========================================================
# COMPLAINT MANAGEMENT
# ===========================================================

@app.route("/complaints", methods=["GET", "POST"])
def complaints():

    if request.method == "POST":

        student_name = request.form["student_name"].strip()

        room_number = request.form["room_number"].strip()

        complaint_text = request.form["complaint"].strip()

        if not student_name or not room_number or not complaint_text:

            flash(
                "All fields are required.",
                "danger"
            )

            return redirect(
                url_for("complaints")
            )

        complaint = Complaint(

            student_name=student_name,

            room_number=room_number,

            complaint=complaint_text,

            status="Pending"

        )

        db.session.add(complaint)

        db.session.commit()

        flash(
            "Complaint Submitted Successfully!",
            "success"
        )

        return redirect(
            url_for("complaints")
        )

    complaint_list = Complaint.query.order_by(
        Complaint.id.desc()
    ).all()

    return render_template(

        "complaints.html",

        complaints=complaint_list

    )


# ===========================================================
# RESOLVE COMPLAINT
# ===========================================================

@app.route("/complaint/resolve/<int:id>")
def resolve_complaint(id):

    complaint = Complaint.query.get_or_404(id)

    complaint.status = "Resolved"

    db.session.commit()

    flash(
        "Complaint Resolved Successfully!",
        "success"
    )

    return redirect(
        url_for("complaints")
    )


# ===========================================================
# DELETE COMPLAINT
# ===========================================================

@app.route("/complaint/delete/<int:id>")
def delete_complaint(id):

    complaint = Complaint.query.get_or_404(id)

    db.session.delete(complaint)

    db.session.commit()

    flash(
        "Complaint Deleted Successfully!",
        "warning"
    )

    return redirect(
        url_for("complaints")
    )


# ===========================================================
# SEARCH STUDENTS
# ===========================================================

@app.route("/students/search")
def search_students():

    keyword = request.args.get(
        "keyword",
        ""
    )

    students = Student.query.filter(

        (Student.name.contains(keyword))

        |

        (Student.usn.contains(keyword))

        |

        (Student.branch.contains(keyword))

    ).all()

    return render_template(

        "dashboard.html",

        students=students,

        search=keyword,

        total_students=Student.query.count(),

        total_rooms=Room.query.count(),

        occupied_rooms=db.session.query(
            Student.room_number
        ).filter(
            Student.room_number.isnot(None),
            Student.room_number != ""
        ).distinct().count(),

        available_rooms=max(
            Room.query.count() -
            db.session.query(
                Student.room_number
            ).filter(
                Student.room_number.isnot(None),
                Student.room_number != ""
            ).distinct().count(),
            0
        ),

        pending_complaints=Complaint.query.filter_by(
            status="Pending"
        ).count()

    )
    # ===========================================================
# CHART DATA API
# ===========================================================

@app.route("/chart-data")
def chart_data():

    total_rooms = Room.query.count()

    occupied_rooms = db.session.query(
        Student.room_number
    ).filter(
        Student.room_number.isnot(None),
        Student.room_number != ""
    ).distinct().count()

    available_rooms = max(
        total_rooms - occupied_rooms,
        0
    )

    pending_complaints = Complaint.query.filter_by(
        status="Pending"
    ).count()

    resolved_complaints = Complaint.query.filter_by(
        status="Resolved"
    ).count()

    return jsonify({

        "room_labels": [
            "Occupied",
            "Available"
        ],

        "room_values": [
            occupied_rooms,
            available_rooms
        ],

        "complaint_labels": [
            "Pending",
            "Resolved"
        ],

        "complaint_values": [
            pending_complaints,
            resolved_complaints
        ]

    })


# ===========================================================
# EXPORT STUDENTS CSV
# ===========================================================

@app.route("/export/students")
def export_students():

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "USN",
        "Name",
        "Email",
        "Phone",
        "Branch",
        "Semester",
        "Room Number"
    ])

    students = Student.query.order_by(
        Student.name
    ).all()

    for student in students:

        writer.writerow([

            student.usn,

            student.name,

            student.email,

            student.phone,

            student.branch,

            student.semester,

            student.room_number

        ])

    memory = io.BytesIO()

    memory.write(
        output.getvalue().encode("utf-8")
    )

    memory.seek(0)

    return send_file(

        memory,

        as_attachment=True,

        download_name="students.csv",

        mimetype="text/csv"

    )


# ===========================================================
# EXPORT PDF REPORT
# ===========================================================

@app.route("/export/pdf")
def export_pdf():

    buffer = io.BytesIO()

    document = SimpleDocTemplate(buffer)

    data = [[

        "USN",

        "Student Name",

        "Room",

        "Branch",

        "Semester"

    ]]

    students = Student.query.order_by(
        Student.name
    ).all()

    for student in students:

        data.append([

            student.usn,

            student.name,

            student.room_number,

            student.branch,

            str(student.semester)

        ])

    table = Table(data)

    table.setStyle(

        TableStyle([

            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),

            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

            ("ALIGN", (0, 0), (-1, -1), "CENTER"),

            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

            ("FONTSIZE", (0, 0), (-1, -1), 10)

        ])

    )

    document.build([table])

    buffer.seek(0)

    return send_file(

        buffer,

        as_attachment=True,

        download_name="Hostel_Report.pdf",

        mimetype="application/pdf"

    )
    # ===========================================================
# ERROR HANDLERS
# ===========================================================

@app.errorhandler(404)
def page_not_found(error):

    return (

        render_template(

            "error.html",

            error_code=404,

            message="The page you are looking for does not exist."

        ),

        404

    )


@app.errorhandler(500)
def internal_server_error(error):

    db.session.rollback()

    return (

        render_template(

            "error.html",

            error_code=500,

            message="An unexpected error occurred."

        ),

        500

    )


# ===========================================================
# DATABASE RESET (OPTIONAL - DEVELOPMENT ONLY)
# ===========================================================

@app.route("/reset-database")
def reset_database():

    db.drop_all()

    db.create_all()

    flash(

        "Database reset successfully.",

        "success"

    )

    return redirect(

        url_for("dashboard")

    )


# ===========================================================
# HEALTH CHECK
# ===========================================================

@app.route("/health")
def health():

    return jsonify({

        "status": "ok",

        "application": "Hostel Management System"

    })


# ===========================================================
# MAIN
# ===========================================================
import os

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )