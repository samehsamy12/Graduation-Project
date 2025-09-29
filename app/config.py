import os
from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc://sa:r00t.R00T@localhost:1433/equi_care?driver=ODBC+Driver+17+for+SQL+Server"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)
    SESSION_TYPE = 'filesystem'
    JWT_SECRET = 'K8v!rZ#5tM^pW2b@X0qL9&dEzJ$NhfUa'
    JWT_EXPIRATION = timedelta(days=7)
