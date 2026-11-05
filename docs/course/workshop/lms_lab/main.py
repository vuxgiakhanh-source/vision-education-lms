import os
from .app import create_app
from .database import make_engine

engine = make_engine(os.environ.get('LAB_DATABASE_URL', 'sqlite:///./learning.db'))
app = create_app(engine, os.environ['LAB_SECRET'],
                 origins=('http://127.0.0.1:5173', 'http://localhost:5173'))
