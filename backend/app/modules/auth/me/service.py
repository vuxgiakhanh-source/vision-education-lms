from .repository import MeRepository
from .exceptions import UserLockedException, UserNotFoundException
from app.models.user import User
from .schemas import MeResponse
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.database import get_db



class MeService:
    def __init__(self, repository: MeRepository):
        self.repository = repository
    
    def get_me_response(self, user_id: int):
        user = self.repository.find_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        if user.is_active == False:
            raise UserLockedException()
        return create_me_service(user)
def create_me_service(user: User) -> MeResponse:
    return MeResponse(
        id=user.id, 
        full_name=user.full_name, 
        phone_number=user.phone_number,
        role=user.role,
        must_change_password=user.must_change_password, 
        is_active=user.is_active
    )
def get_me_service(db: Session = Depends(get_db)):
    repository = MeRepository(db)
    return MeService(repository)
