import argparse
from datetime import datetime, timedelta, timezone
import os
from jose import jwt
from .database import make_engine, session_factory
from .models import Base, Classroom, Membership, User

parser = argparse.ArgumentParser(description='Dữ liệu/token giả cho lab cục bộ, không dùng DB sản phẩm')
parser.add_argument('action', choices=['init', 'token'])
parser.add_argument('--user', type=int, default=1)
args = parser.parse_args()
secret = os.environ.get('LAB_SECRET', '')
if len(secret) < 32:
    parser.error('Đặt LAB_SECRET ngẫu nhiên ít nhất 32 ký tự trước khi chạy')
if args.action == 'token':
    if args.user not in {1, 2, 3, 4}:
        parser.error('Fixture có user 1, 2, 3, 4')
    print(jwt.encode({'sub': str(args.user),
                      'exp': datetime.now(timezone.utc) + timedelta(minutes=30)}, secret, algorithm='HS256'))
else:
    url = os.environ.get('LAB_DATABASE_URL', 'sqlite:///./learning.db')
    if not url.startswith('sqlite:'):
        parser.error('CLI init chỉ tạo SQLite học; MySQL cần migration do người học review')
    engine = make_engine(url)
    Base.metadata.create_all(engine)
    with session_factory(engine)() as db:
        if db.get(User, 1):
            parser.error('Đã có fixture; không reset hoặc ghi đè dữ liệu')
        db.add_all([User(id=1, name='Cô mẫu', role='teacher'),
                    User(id=2, name='An mẫu', role='student'),
                    User(id=3, name='Bình mẫu', role='student'),
                    User(id=4, name='Đã khóa', role='student', active=0)])
        db.flush()
        classroom = Classroom(title='Lớp mẫu', teacher_id=1)
        db.add(classroom)
        db.flush()
        db.add(Membership(class_id=classroom.id, student_id=2))
        db.commit()
    print('Đã tạo fixture SQLite học. User 2 thuộc lớp; user 3 không thuộc lớp.')
