from sqlalchemy.orm import Session
from app.models.user import User
class MeRepository:
    def __init__(self, db:Session):
        self.db = db
    
    def find_user_by_id(
        self,
        user_id: int
    ):
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )
    