from app import db, app
from app.models import User

with app.app_context():
    # admin = User(
    #     first_name="ADMIN",
    #     last_name="Admin",
    #     student_id="00000-001",
    #     course="-",
    #     year_level="-",
    #     username='admin',
    #     password="pbkdf2:sha256:600000$YZDx6yNdjZWkV9oq$b688db58b78f9269ce397a5a92cec765c294e35517eb77f379dfffd7977a6ca1"
    # )
    blonde = User(
        first_name="System",
        last_name="User 1",
        student_id="00000-002",
        course="-",
        year_level="-",
        username='Blonde Hair'
    )

    not_uniform = User(
        first_name="System",
        last_name="User 2",
        student_id="00000-003",
        course="-",
        year_level="-",
        username='In Proper Uniform'
    )

    db.session.add_all([blonde, not_uniform])
    db.session.commit()
