from sqlalchemy.orm import Session
from app.models.user import User
class AuthRepository:
    def __init__(self, db: Session):
        self.db = db
    def find_user_by_phone_number(
            self,
            phone_number: str
    ):
        return (
            self.db.query(User)
            .filter(User.phone_number == phone_number)
            .first()
        )        
    def find_user_by_id(
        self,
        user_id: int
    ):
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )
    
