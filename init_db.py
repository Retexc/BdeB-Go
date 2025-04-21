# init_db.py
from admin import app, db, User

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        u = User(username="admin")
        u.set_password("adminbdeb")
        db.session.add(u)
        db.session.commit()
        print("🔐 Created default admin user")
    else:
        print("✅ Admin user already exists")
