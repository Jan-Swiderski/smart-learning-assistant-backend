class Config:
    SECRET_KEY = 'bardzo tajny klucz'
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/test_mydatabase'
    JWT_SECRET_KEY = 'jwt_secret_key'
class DevelopmentConfig(Config):
    DEBUG = True
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/test_mydatabase'

class ProductionConfig(Config):
    pass