from app import db, app
from app.models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User(
        first_name="SASO",
        last_name="Admin",
        student_id="00000-004",
        course="-",
        year_level="-",
        username='saso',
        password=generate_password_hash("password")
    )
    # blonde = User(
    #     first_name="System",
    #     last_name="User 1",
    #     student_id="00000-002",
    #     course="-",
    #     year_level="-",
    #     username='Blonde Hair'
    # )

    # not_uniform = User(
    #     first_name="System",
    #     last_name="User 2",
    #     student_id="00000-003",
    #     course="-",
    #     year_level="-",
    #     username='In Proper Uniform'
    # )

    db.session.add(admin)
    db.session.commit()
