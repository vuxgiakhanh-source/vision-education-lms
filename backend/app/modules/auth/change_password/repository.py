from app.models.user import User
from sqlalchemy.orm import Session

class ChangePasswordRepository:
    def __init__(self, db: Session):
        self.db = db
    def find_user_by_id(self, user_id: int):
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )
    def change_password(self, user: User, new_hashed_password):
        user.hashed_password = new_hashed_password
        user.must_change_password = False
        self.db.commit()

