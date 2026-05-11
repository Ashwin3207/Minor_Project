from app import create_app, db
from app.models import StudentProfile, User

app = create_app()
with app.app_context():
    # Get the test student's profile
    user = User.query.filter_by(username='testStudent2026').first()
    if user:
        profile = StudentProfile.query.filter_by(user_id=user.id).first()
        if profile:
            print(f"✅ Profile found for {user.username}")
            print(f"   Internship: {profile.internship_details}")
            print(f"   NPTEL: {profile.nptel}")
            print(f"   FYP: {profile.final_year_project}")
        else:
            print("❌ No profile found")
    else:
        print("❌ User not found")
