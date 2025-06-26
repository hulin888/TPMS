from app.core.models.database import DATABASE
from app.admin.auth import AuthHandler


def db_session():
    database = DATABASE()
    return database
def auth_handler():
    auth_handler = AuthHandler()    
    return auth_handler