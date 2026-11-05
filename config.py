import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')


def _database_uri():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        return f"sqlite:///{BASE_DIR / 'sweetdreams.db'}"
    if database_url.startswith('mysql://'):
        return database_url.replace('mysql://', 'mysql+pymysql://', 1)
    return database_url


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'sweetdreams-dev-secret')
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = os.getenv('ENABLE_CSRF', 'false').lower() == 'true'
    UPLOAD_FOLDER = str(BASE_DIR / 'static' / 'img' / 'products')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
