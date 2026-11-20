from secrets import token_urlsafe

from sqlalchemy import select

from app.database.database import SessionLocal
from app.core.security import hash_password
from app.core.enums.user_role import UserRole
from app.models.student import Student
from app.models.user import User


DEMO_PHONE = "0833882007"
DEMO_NAME = "Test User"
DEMO_GRADE = 12


def main() -> None:
    password = None
    with SessionLocal.begin() as db:
        user = db.scalar(select(User).where(User.phone_number == DEMO_PHONE).with_for_update())
        if user is None:
            password = token_urlsafe(18)
            user = User(
                full_name=DEMO_NAME,
                phone_number=DEMO_PHONE,
                hashed_password=hash_password(password),
                role=UserRole.STUDENT,
                must_change_password=True,
            )
            db.add(user)
            db.flush()
        elif user.role != UserRole.STUDENT or user.full_name != DEMO_NAME:
            raise RuntimeError("The demo phone belongs to a different account.")

        if db.get(Student, user.id) is None:
            db.add(Student(user_id=user.id, grade=DEMO_GRADE))

    print(f"Demo student: {DEMO_PHONE}")
    if password is not None:
        print(f"Initial password (shown once): {password}")
    else:
        print("Existing account and password preserved.")


if __name__ == "__main__":
    main()
