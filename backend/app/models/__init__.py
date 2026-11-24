"""Import mọi model để Base.metadata biết đủ bảng.

Alembic autogenerate/check và Base.metadata.create_all (test SQLite) chỉ thấy những bảng
đã được import. Thêm model mới (ví dụ exam) thì thêm tên module vào dòng dưới,
đừng import thủ công từng model trong alembic/env.py.
"""

from app.models import classroom, exam, schedule, student, user  # noqa: F401
