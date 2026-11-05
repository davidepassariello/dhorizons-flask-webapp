"""Initialize a clean local SQLite database (never commit it)."""
from app import app, db
with app.app_context():
    db.create_all()
    print('Local database initialized.')
