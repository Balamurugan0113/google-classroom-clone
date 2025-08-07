import os

class Config:
    SECRET_KEY = 'Bala@0002'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Bala%400002@localhost/google_classroom'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
