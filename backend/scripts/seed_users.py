from app.database.database import SessionLocal
from app.core.security import hash_password
from app.core.enums.user_role import UserRole
from app.models.user import User


db = SessionLocal()

user = User(
    full_name="Test User",
    phone_number="0833882007",
    hashed_password=hash_password("123456"),
    role=UserRole.STUDENT,
)

db.add(user)
db.commit()
db.refresh(user)

db.close()