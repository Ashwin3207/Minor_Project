from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Add the three new columns
        db.session.execute(text('ALTER TABLE student_profiles ADD COLUMN internship_details TEXT'))
        db.session.execute(text('ALTER TABLE student_profiles ADD COLUMN nptel TEXT'))
        db.session.execute(text('ALTER TABLE student_profiles ADD COLUMN final_year_project TEXT'))
        db.session.commit()
        print("✅ Successfully added new columns to student_profiles table!")
    except Exception as e:
        error_msg = str(e).lower()
        if "duplicate column" in error_msg or "already exists" in error_msg:
            print("✅ Columns already exist")
        else:
            print(f"❌ Error: {str(e)}")
            raise
