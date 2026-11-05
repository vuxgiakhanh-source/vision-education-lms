from fastapi import Depends, FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from .database import session_factory
from .models import User
from .repository import ClassRepository
from .schemas import ClassInput, ClassOutput
from .service import ClassService, Forbidden, NotFound
from .unit_of_work import SqlTransaction


def create_app(engine, secret: str, origins=()):
    if len(secret) < 32:
        raise ValueError('LAB_SECRET cần ít nhất 32 ký tự ngẫu nhiên cho môi trường học')
    app = FastAPI(title='LMS learning workshop')
    app.add_middleware(CORSMiddleware, allow_origins=list(origins),
                       allow_methods=['GET', 'POST', 'PATCH', 'PUT'],
                       allow_headers=['Authorization', 'Content-Type'])
    sessions = session_factory(engine)
    bearer = HTTPBearer(auto_error=False)

    def get_db():
        with sessions() as db:
            yield db

    def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
                     db=Depends(get_db)):
        unauthorized = HTTPException(401, 'Xác thực không hợp lệ',
                                     headers={'WWW-Authenticate': 'Bearer'})
        if credentials is None:
            raise unauthorized
        try:
            payload = jwt.decode(credentials.credentials, secret, algorithms=['HS256'],
                                 options={'require_exp': True, 'require_sub': True})
            subject = payload['sub']
            if not isinstance(subject, str) or not subject.isascii() or not subject.isdigit():
                raise unauthorized
            actor = db.get(User, int(subject))
        except (JWTError, ValueError):
            raise unauthorized
        if actor is None:
            raise unauthorized
        if not actor.active or actor.role not in {'teacher', 'student'}:
            raise HTTPException(403, 'Tài khoản không được phép dùng bài học này')
        return actor

    def service(db=Depends(get_db)):
        return ClassService(ClassRepository(db), SqlTransaction(db))

    def translate(call):
        try:
            return call()
        except Forbidden:
            raise HTTPException(403, 'Không có quyền thực hiện') from None
        except NotFound:
            raise HTTPException(404, 'Không tìm thấy lớp trong phạm vi được phép') from None

    @app.get('/health')
    def health():
        return {'status': 'ok'}

    @app.get('/classes', response_model=list[ClassOutput])
    def list_classes(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                     actor=Depends(current_user), classes=Depends(service)):
        return classes.list_visible(actor, page, page_size)

    @app.post('/classes', response_model=ClassOutput, status_code=201)
    def create_class(payload: ClassInput, actor=Depends(current_user), classes=Depends(service)):
        return translate(lambda: classes.create(actor, payload.title))

    @app.get('/classes/{class_id}', response_model=ClassOutput)
    def read_class(class_id: int = Path(gt=0), actor=Depends(current_user), classes=Depends(service)):
        return translate(lambda: classes.read(actor, class_id))

    @app.patch('/classes/{class_id}', response_model=ClassOutput)
    def rename_class(payload: ClassInput, class_id: int = Path(gt=0),
                     actor=Depends(current_user), classes=Depends(service)):
        return translate(lambda: classes.rename(actor, class_id, payload.title))

    from .workflow import install_workflow
    install_workflow(app, get_db, current_user)
    return app
