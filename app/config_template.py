class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/test_mydatabase'
        
    DEV_DEBUG = True
    # DEV_DEBUG = False
    # INIT_DB = True
    INIT_DB = False
