from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    def __init__(self):
        self.mysql_user = os.getenv("MYSQL_USER")
        self.mysql_password = os.getenv("MYSQL_PASSWORD")
        self.mysql_database = os.getenv("MYSQL_DATABASE")
        self.database_url = f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@localhost:3306/{self.mysql_database}"
        self.secret_key = os.getenv("SECRET_KEY")
        self.access_token_expire_minutes =  int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
settings = Settings()